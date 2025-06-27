from kavenegar import *
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import hashlib
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from .models import DeviceToken, CustomUser

# Kavenegar API key from settings
KAVENEGAR_API_KEY = getattr(settings, 'KAVENEGAR_API_KEY', '454F4B50684B70626163446F6D4D6E2B496A7550586677746777444D543271777966303431534D486931383D')
KAVENEGAR_SENDER = getattr(settings, 'KAVENEGAR_SENDER', '2000660110')

def generate_verification_code():
    """Generate a random 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_sms(phone_number, code):
    """Send verification SMS to user's phone number"""
    try:
        api = KavenegarAPI(KAVENEGAR_API_KEY)
        params = {
            'receptor': phone_number,
            'sender': KAVENEGAR_SENDER,
            'message': f"کد تایید شما: {code}",
            'type': 'sms'
        }
        response = api.sms_send(params)
        return True, response
    except APIException as e:
        return False, str(e)
    except HTTPException as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def is_verification_code_expired(created_at, expiry_minutes=2):
    """Check if verification code is expired"""
    if not created_at:
        return True
    
    now = timezone.now()
    if created_at.tzinfo is None:
        created_at = timezone.make_aware(created_at)
    
    expiry_time = created_at + timedelta(minutes=expiry_minutes)
    return now > expiry_time


def generate_device_token_hash(user_id, device_info):
    """Generate a unique hash for device token"""
    device_string = f"{user_id}_{device_info.get('device_name', '')}_{device_info.get('device_type', '')}_{timezone.now().timestamp()}"
    return hashlib.sha256(device_string.encode()).hexdigest()

def create_jwt_tokens_for_device(user, device_info):
    """Create JWT tokens for a specific device"""
    # Generate refresh token
    refresh = RefreshToken.for_user(user)
    
    # Create device token record
    token_hash = generate_device_token_hash(user.id, device_info)
    expires_at = timezone.now() + timedelta(days=7)  # 7 days for refresh token
    
    device_token = DeviceToken.objects.create(
        user=user,
        device_name=device_info.get('device_name'),
        device_type=device_info.get('device_type', 'other'),
        token_hash=token_hash,
        expires_at=expires_at
    )
    
    # Add custom claims to tokens
    refresh['device_id'] = str(device_token.id)
    refresh['device_name'] = device_info.get('device_name', '')
    refresh['device_type'] = device_info.get('device_type', 'other')
    
    access_token = refresh.access_token
    access_token['device_id'] = str(device_token.id)
    access_token['device_name'] = device_info.get('device_name', '')
    access_token['device_type'] = device_info.get('device_type', 'other')
    
    return {
        'access': str(access_token),
        'refresh': str(refresh),
        'device_id': str(device_token.id),
        'device_name': device_info.get('device_name', ''),
        'device_type': device_info.get('device_type', 'other')
    }

def revoke_device_token(device_id):
    """Revoke a specific device token"""
    try:
        device_token = DeviceToken.objects.get(id=device_id)
        device_token.is_active = False
        device_token.save()
        return True
    except DeviceToken.DoesNotExist:
        return False

def revoke_all_user_tokens(user):
    """Revoke all tokens for a user"""
    DeviceToken.objects.filter(user=user, is_active=True).update(is_active=False)

def get_user_active_devices(user):
    """Get all active devices for a user"""
    return DeviceToken.objects.filter(user=user, is_active=True).order_by('-last_used')

def update_device_last_used(device_id):
    """Update the last used timestamp for a device"""
    try:
        device_token = DeviceToken.objects.get(id=device_id)
        device_token.save()  # This will update last_used due to auto_now=True
        return True
    except DeviceToken.DoesNotExist:
        return False

def cleanup_expired_tokens():
    """Clean up expired device tokens"""
    now = timezone.now()
    expired_tokens = DeviceToken.objects.filter(expires_at__lt=now, is_active=True)
    expired_tokens.update(is_active=False)
    return expired_tokens.count()

def send_login_notification_sms(phone_number, device_info):
    """Send login notification SMS when user logs in from new device"""
    try:
        api = KavenegarAPI(KAVENEGAR_API_KEY)
        device_name = device_info.get('device_name', 'دستگاه جدید')
        device_type = device_info.get('device_type', 'other')
        
        # Persian device type mapping
        device_type_persian = {
            'mobile': 'موبایل',
            'tablet': 'تبلت', 
            'desktop': 'دسکتاپ',
            'web': 'وب',
            'other': 'دستگاه'
        }.get(device_type, 'دستگاه')
        
        message = f"ورود جدید از {device_type_persian} {device_name} در {timezone.now().strftime('%Y/%m/%d %H:%M')}"
        
        params = {
            'receptor': phone_number,
            'sender': KAVENEGAR_SENDER,
            'message': message,
            'type': 'sms'
        }
        response = api.sms_send(params)
        return True, response
    except Exception as e:
        return False, str(e)
