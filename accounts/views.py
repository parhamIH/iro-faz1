
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login

from .models import Provider, Profile ,  CustomUser
from .permissions import IsAdmin, IsProvider, IsAdminOrProvider
from .serializers import ChangePasswordSerializer , ResetPasswordConfirmSerializer,UserRegisterSerializer,UserLoginSerializer


"""
ویوهای مربوط به مدیریت کاربران، ادمین‌ها و ارائه‌دهندگان
هر ویو با توجه به سطح دسترسی تعریف شده، قابل استفاده خواهد بود
"""

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



class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)  # لاگین با session-based auth (اختیاری)
            return Response({'message': 'ورود موفقیت‌آمیز بود.', 'user_id': user.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
