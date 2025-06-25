from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from .models import * 
from .services import *


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'full_name', 'date_of_birth', 'phone_number', 'is_phone_verified',
            'national_id', 'economic_code', 'is_verified', 'is_active', 'is_staff'
        ]
        read_only_fields = ['is_verified', 'is_active', 'is_staff']
    # add kavenegar or more sms providers 
    def validate_phone_number(self, value) :
        if not value:
            raise serializers.ValidationError("شماره تلفن الزامی است.")
        if not value.startswith('+98') and not value.startswith('09'):
            raise serializers.ValidationError("شماره باید با +98 یا 09 شروع شود.")
        return value

    def validate_national_id(self, value):
        if value and len(value) != 10:
            raise serializers.ValidationError("کد ملی باید دقیقاً 10 رقم باشد.")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['full_identity'] = f"{instance.full_name} ({instance.national_id})" if instance.national_id else instance.full_name
        return rep
class AddressSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_phone = serializers.CharField(source='client.phone_number', read_only=True)

    class Meta: 
        model = Address
        fields = ['id', 'title_address', 'province', 'city', 'full_address', 'postcode', 'client_name', 'client_phone']
    
    def validate_postcode(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("کد پستی باید فقط شامل ارقام باشد.")
        return value
class NotificationSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'related_url', 'created_at', 'user_phone']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        type_display = dict(Notification.NOTIFICATION_TYPES).get(instance.notification_type, "نامشخص")
        rep['notification_type_display'] = type_display
        return rep

class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='client.full_name', read_only=True)
    email = serializers.EmailField(source='client.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'legal_info', 'refund_method', 'full_name', 'email']

    def validate_refund_method(self, value):
        if value and len(value) < 3:
            raise serializers.ValidationError("روش بازگرداندن پول باید حداقل ۳ حرف باشد.")
        return value
class ProviderSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='provider.phone_number', read_only=True)
    email = serializers.EmailField(source='provider.email', read_only=True)

    class Meta:
        model = Provider
        fields = [
            'id', 'company_name', 'company_registration_number', 'company_description',
            'is_active', 'created_at', 'updated_at', 'phone_number', 'email'
        ]
class FavProductListSerializer(serializers.ModelSerializer):
    products = serializers.StringRelatedField(many=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)

    class Meta:
        model = FavProductList
        fields = ['id', 'products', 'created_at', 'updated_at', 'client_name']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['total_products'] = instance.products.count()
        return rep
class OfferCodeSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = OfferCode
        fields = ['id', 'title', 'code', 'created_at', 'users']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['used_by_count'] = instance.users.count()
        return rep


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)


    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone_number', 'email', 'password']

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("شماره تلفن قبلا استفاده شده است.")
        if not value.startswith('+98') and not value.startswith('09'):
            raise serializers.ValidationError("شماره باید با +98 یا 09 شروع شود.")
        return value
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("ایمیل قبلا استفاده شده است.")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get('phone_number')
        email = data.get('email')
        password = data.get('password')

        if not phone and not email:
            raise serializers.ValidationError(_("باید شماره تلفن یا ایمیل وارد شود."))

        try:
            user = None
            if phone:
                user = CustomUser.objects.get(phone_number=phone)
            elif email:
                user = CustomUser.objects.get(email=email)

            if not user.check_password(password):
                raise serializers.ValidationError(_("اطلاعات ورود نادرست است."))

            if not user.is_active:
                raise serializers.ValidationError(_("حساب کاربری غیرفعال است."))

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            data['user'] = user
            return data

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(_("کاربری با این مشخصات یافت نشد."))
        except serializers.ValidationError as ve:
            raise ve  # همون خطای اصلی رو دوباره بنداز
        except Exception as e:
            raise serializers.ValidationError(_("خطای غیرمنتظره‌ای رخ داد."))  # فقط پیام عمومی بده

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'date_of_birth', 'national_id', 'economic_code']

    def validate_national_id(self, value):
        if value and len(value) != 10:
            raise serializers.ValidationError("کد ملی باید دقیقاً 10 رقم باشد.")
        return value
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context['request'].user
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not user.check_password(old_password):
            raise serializers.ValidationError({'old_password': 'رمز فعلی اشتباه است.'})

        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'رمز جدید با تکرار آن مطابقت ندارد.'})

        if old_password == new_password:
            raise serializers.ValidationError({'new_password': 'رمز جدید نباید با رمز قبلی یکسان باشد.'})

        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
class ResetPasswordRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        try:
            user = CustomUser.objects.get(phone_number=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("کاربری با این شماره تلفن یافت نشد.")
        return value
class ResetPasswordConfirmSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    verification_code = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        phone = data.get('phone_number')
        code = data.get('verification_code')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        try:
            user = CustomUser.objects.get(phone_number=phone, verification_code=code)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("کد تأیید یا شماره تلفن نادرست است.")

        if new_password != confirm_password:
            raise serializers.ValidationError("رمز جدید با تکرار آن یکسان نیست.")

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.verification_code = None  # حذف کد بعد از استفاده
        user.save()
        return user

class SMSVerificationSerializer(serializers.Serializer):
    """Serializer for SMS verification request"""
    phone_number = serializers.CharField(required=True)
    
    def validate_phone_number(self, value):
        if not value.startswith('+98') and not value.startswith('09'):
            raise serializers.ValidationError("شماره باید با +98 یا 09 شروع شود.")
        return value

class SMSVerificationConfirmSerializer(serializers.Serializer):
    """Serializer for SMS verification confirmation"""
    phone_number = serializers.CharField(required=True)
    verification_code = serializers.CharField(required=True, max_length=6)
    
    def validate(self, data):
        phone_number = data.get('phone_number')
        verification_code = data.get('verification_code')
        
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("کاربری با این شماره تلفن یافت نشد.")
        
        if not user.verification_code:
            raise serializers.ValidationError("کد تأیید ارسال نشده است.")
        
        if is_verification_code_expired(user.verification_code_created_at):
            raise serializers.ValidationError("کد تأیید منقضی شده است.")
        
        if user.verification_code != verification_code:
            raise serializers.ValidationError("کد تأیید نادرست است.")
        
        data['user'] = user
        return data

class DeviceInfoSerializer(serializers.Serializer):
    """Serializer for device information"""
    device_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    device_type = serializers.ChoiceField(
        choices=[
            ('mobile', 'موبایل'),
            ('tablet', 'تبلت'),
            ('desktop', 'دسکتاپ'),
            ('web', 'وب'),
            ('other', 'سایر'),
        ],
        default='other'
    )

class JWTLoginSerializer(serializers.Serializer):
    """Serializer for JWT login with SMS verification"""
    phone_number = serializers.CharField(required=True)
    verification_code = serializers.CharField(required=True, max_length=6)
    device_info = DeviceInfoSerializer(required=False)
    
    def validate(self, data):
        phone_number = data.get('phone_number')
        verification_code = data.get('verification_code')
        
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("کاربری با این شماره تلفن یافت نشد.")
        
        if not user.verification_code:
            raise serializers.ValidationError("کد تأیید ارسال نشده است.")
        
        if is_verification_code_expired(user.verification_code_created_at):
            raise serializers.ValidationError("کد تأیید منقضی شده است.")
        
        if user.verification_code != verification_code:
            raise serializers.ValidationError("کد تأیید نادرست است.")
        
        if not user.is_active:
            raise serializers.ValidationError("حساب کاربری غیرفعال است.")
        
        data['user'] = user
        return data

class JWTRefreshSerializer(serializers.Serializer):
    """Serializer for JWT token refresh"""
    refresh = serializers.CharField(required=True)
    
    def validate_refresh(self, value):
        try:
            # Validate refresh token
            refresh = RefreshToken(value)
            return value
        except Exception:
            raise serializers.ValidationError("توکن نامعتبر است.")

class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer for device token model"""
    class Meta:
        model = DeviceToken
        fields = ['id', 'device_name', 'device_type', 'is_active', 'last_used', 'created_at', 'expires_at']
        read_only_fields = ['id', 'is_active', 'last_used', 'created_at', 'expires_at']

class UserDevicesSerializer(serializers.ModelSerializer):
    """Serializer for user's active devices"""
    devices = DeviceTokenSerializer(source='device_tokens', many=True, read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'phone_number', 'devices']

class LogoutSerializer(serializers.Serializer):
    """Serializer for logout (revoke all tokens)"""
    revoke_all = serializers.BooleanField(default=False, required=False)

class RevokeDeviceSerializer(serializers.Serializer):
    """Serializer for revoking specific device token"""
    device_id = serializers.UUIDField(required=True)
    
    def validate_device_id(self, value):
        try:
            device_token = DeviceToken.objects.get(id=value)
            if not device_token.is_active:
                raise serializers.ValidationError("این دستگاه قبلاً غیرفعال شده است.")
            return value
        except DeviceToken.DoesNotExist:
            raise serializers.ValidationError("دستگاه یافت نشد.")
