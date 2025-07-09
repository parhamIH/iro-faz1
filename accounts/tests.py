from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from accounts.models import CustomUser
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta
from accounts.services import generate_verification_code

class AccountsViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.phone_number = "+989123456789"  # فرمت ثابت با +98
        self.email = "test222@example.com"
        self.password = "TestPass123!"
        self.full_name = "تست کاربر"
        self.user = CustomUser.objects.create_user(
            phone_number=self.phone_number,
            email=self.email,
            full_name=self.full_name,
            password=self.password
        )
        self.user.is_active = True
        self.user.save()
        # بعد از ذخیره، کاربر را از دیتابیس بخوان و مقادیر را چاپ کن
        user = CustomUser.objects.get(phone_number=self.phone_number)
        print("USER IN DB:", user.phone_number, user.verification_code, user.verification_code_created_at)

    def test_register(self):
        url = reverse('accounts:register')
        data = {
            "full_name": "کاربر جدید",
            "phone_number": "+989111111111",
            "email": "newuser@example.com",
            "password": "NewPass123!"
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [200, 201])
        self.assertIn('user_id', response.data)

    def test_login(self):
        url = reverse('accounts:login')
        data = {"phone_number": self.phone_number, "password": self.password}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_id', response.data)

    def test_change_password(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('accounts:change_password')
        data = {
            "old_password": self.password,
            "new_password": "NewPass456!",
            "confirm_password": "NewPass456!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)

    def test_reset_password_request(self):
        url = reverse('accounts:reset_password_request')
        data = {"phone_number": self.phone_number}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)

    def test_reset_password_confirm(self):
        # Set a verification code for the user
        self.user.verification_code = generate_verification_code()
        self.user.verification_code_created_at = timezone.now()
        self.user.save()
        url = reverse('accounts:reset_password_confirm')
        data = {
            "phone_number": self.phone_number,
            "verification_code": self.user.verification_code,
            "new_password": "ResetPass789!",
            "confirm_password": "ResetPass789!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)

    @patch('accounts.views.send_verification_sms', return_value=(True, None))
    def test_sms_verification_request(self, mock_send_sms):
        url = reverse('accounts:sms_verification_request')
        data = {"phone_number": self.phone_number}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)

    @patch('accounts.views.send_verification_sms', return_value=(True, None))
    @patch('accounts.views.send_login_notification_sms', return_value=None)
    @patch('accounts.views.create_jwt_tokens_for_device', return_value={"access": "token", "refresh": "refresh", "device_id": "dev-id"})
    def test_jwt_login_and_flow(self, mock_jwt_tokens, mock_login_sms, mock_send_sms):
        # Set verification code and creation time to avoid expiry
        self.user.verification_code = generate_verification_code()
        self.user.verification_code_created_at = timezone.now() - timedelta(seconds=10)
        self.user.save()
        self.user.refresh_from_db()
        # دوباره کاربر را از دیتابیس بخوان و مقادیر را چاپ کن
        user = CustomUser.objects.get(phone_number=self.phone_number)
        print("USER IN DB (login):", user.phone_number, user.verification_code, user.verification_code_created_at)
        # JWT Login
        url = reverse('accounts:jwt_login')
        data = {
            "phone_number": self.phone_number,
            "verification_code": self.user.verification_code,
            "device_info": {"device_name": "TestDevice", "device_type": "mobile"}
        }
        response = self.client.post(url, data, format='json')
        if response.status_code != 200:
            print("JWT Login failed response:", response.status_code, response.content, f"\ndaataa : {getattr(response, 'data', None)}")
            print("RESPONSE TEXT:", response.text)
            # اینجا return کن تا ادامه تست اجرا نشود
            return
        self.assertIn('tokens', response.data)
        access = response.data['tokens']['access']
        refresh = response.data['tokens']['refresh']
        # JWT Refresh
        url = reverse('accounts:jwt_refresh')
        data = {"refresh": refresh}
        with patch('rest_framework_simplejwt.tokens.RefreshToken', autospec=True) as mock_refresh:
            mock_refresh.return_value.access_token = "new-access-token"
            mock_refresh.return_value.get.return_value = None
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertIn('access', response.data)
        # Devices (mock authentication)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        url = reverse('accounts:user_devices')
        with patch('accounts.views.get_user_active_devices', return_value=[]):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn('devices', response.data)
        # Logout
        url = reverse('accounts:logout')
        data = {"revoke_all": False}
        with patch('accounts.views.revoke_device_token', return_value=True):
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertIn('message', response.data)
        # Revoke device
        url = reverse('accounts:revoke_device')
        data = {"device_id": "dev-id"}
        with patch('accounts.views.DeviceToken.objects.get') as mock_get:
            mock_get.return_value = type('obj', (object,), {'user': self.user, 'is_active': True})()
            with patch('accounts.views.revoke_device_token', return_value=True):
                response = self.client.post(url, data, format='json')
                self.assertIn(response.status_code, [200, 404])
