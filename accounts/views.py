from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import login
from django.conf import settings
from .models import Provider, Profile ,  CustomUser, DeviceToken
from .permissions import IsAdmin, IsProvider, IsAdminOrProvider
from .serializers import (
    ChangePasswordSerializer, ResetPasswordConfirmSerializer, UserRegisterSerializer, 
    UserLoginSerializer, SMSVerificationSerializer, SMSVerificationConfirmSerializer,
    JWTLoginSerializer, JWTRefreshSerializer, DeviceTokenSerializer, UserDevicesSerializer,
    LogoutSerializer, RevokeDeviceSerializer, DeviceInfoSerializer
)
from .services import (
    generate_verification_code, send_verification_sms, create_jwt_tokens_for_device,
    revoke_device_token, revoke_all_user_tokens, get_user_active_devices,
    update_device_last_used, send_login_notification_sms
)

"""
ویوهای مربوط به مدیریت کاربران، ادمین‌ها و ارائه‌دهندگان
هر ویو با توجه به سطح دسترسی تعریف شده، قابل استفاده خواهد بود
"""

class SMSVerificationRequestView(APIView):
    """Request SMS verification code"""
    def post(self, request):
        serializer = SMSVerificationSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            
            # Check if user exists
            try:
                user = CustomUser.objects.get(phone_number=phone_number)
            except CustomUser.DoesNotExist:
                return Response(
                    {'error': 'کاربری با این شماره تلفن یافت نشد.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Generate verification code
            code = generate_verification_code()
            user.verification_code = code
            user.verification_code_created_at = timezone.now()
            user.save()
            
            # Check if we're in development mode
            if getattr(settings, 'DEBUG', False) and getattr(settings, 'BYPASS_SMS_IN_DEV', False):
                # In development, just return the code without sending SMS
                return Response({
                    'message': 'کد تأیید در حالت توسعه: ' + code,
                    'phone_number': phone_number,
                    'verification_code': code,  # Only in development!
                    'development_mode': True
                }, status=status.HTTP_200_OK)
            
            # Send SMS
            success, response = send_verification_sms(phone_number, code)
            
            if success:
                return Response({
                    'message': 'کد تأیید ارسال شد.',
                    'phone_number': phone_number
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'خطا در ارسال پیامک.',
                    'details': response
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JWTLoginView(APIView):
    """JWT login with SMS verification"""
    def post(self, request):
        serializer = JWTLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            device_info = serializer.validated_data.get('device_info', {})
            
            # Clear verification code after successful login
            user.verification_code = None
            user.verification_code_created_at = None
            user.is_phone_verified = True
            user.save()
            
            # Create JWT tokens for device
            tokens = create_jwt_tokens_for_device(user, device_info)
            
            # Send login notification SMS
            if user.phone_number:
                send_login_notification_sms(user.phone_number, device_info)
            
            return Response({
                'message': 'ورود موفقیت‌آمیز بود.',
                'user': {
                    'id': user.id,
                    'full_name': user.full_name,
                    'phone_number': user.phone_number,
                    'email': user.email,
                    'is_phone_verified': user.is_phone_verified
                },
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JWTRefreshView(APIView):
    """Refresh JWT token"""
    def post(self, request):
        serializer = JWTRefreshSerializer(data=request.data)
        if serializer.is_valid():
            try:
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken(serializer.validated_data['refresh'])
                
                # Update device last used
                device_id = refresh.get('device_id')
                if device_id:
                    update_device_last_used(device_id)
                
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': 'خطا در تمدید توکن.',
                    'details': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDevicesView(APIView):
    """Get user's active devices"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        devices = get_user_active_devices(request.user)
        serializer = DeviceTokenSerializer(devices, many=True)
        return Response({
            'devices': serializer.data,
            'total_devices': devices.count()
        }, status=status.HTTP_200_OK)

class RevokeDeviceView(APIView):
    """Revoke specific device token"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = RevokeDeviceSerializer(data=request.data)
        if serializer.is_valid():
            device_id = serializer.validated_data['device_id']
            
            # Check if device belongs to user
            try:
                device_token = DeviceToken.objects.get(id=device_id, user=request.user)
            except DeviceToken.DoesNotExist:
                return Response({
                    'error': 'دستگاه یافت نشد یا متعلق به شما نیست.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            success = revoke_device_token(device_id)
            if success:
                return Response({
                    'message': 'دستگاه با موفقیت غیرفعال شد.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'خطا در غیرفعال‌سازی دستگاه.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """Logout and revoke tokens"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            revoke_all = serializer.validated_data.get('revoke_all', False)
            
            if revoke_all:
                # Revoke all user tokens
                revoke_all_user_tokens(request.user)
                message = 'تمام دستگاه‌ها غیرفعال شدند.'
            else:
                # Get device ID from token
                device_id = request.auth.get('device_id') if hasattr(request, 'auth') and request.auth else None
                if device_id:
                    revoke_device_token(device_id)
                    message = 'دستگاه فعلی غیرفعال شد.'
                else:
                    message = 'خروج انجام شد.'
            
            return Response({
                'message': message
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)  # لاگین با session-based auth (اختیاری)
            return Response({'message': 'ورود موفقیت‌آمیز بود.', 'user_id': user.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'رمز عبور با موفقیت تغییر کرد.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from .serializers import ResetPasswordRequestSerializer
from django.utils.crypto import get_random_string

class ResetPasswordRequestView(APIView):
    def post(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']
            user = CustomUser.objects.get(phone_number=phone)
            # ایجاد کد تأیید
            code = get_random_string(length=6, allowed_chars='0123456789')
            user.verification_code = code
            user.save()
            # (اینجا باید کد را SMS یا Email کنید)
            return Response({'message': 'کد تأیید ارسال شد.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordConfirmView(APIView):
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'رمز جدید با موفقیت ثبت شد.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'ثبت‌نام با موفقیت انجام شد.', 'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


