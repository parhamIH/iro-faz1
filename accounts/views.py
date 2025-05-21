from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, ClientProfile, ProviderProfile, Address
from .serializers import (
    CustomUserSerializer, 
    ClientProfileSerializer, 
    ProviderProfileSerializer, 
    AddressSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    ChangePasswordSerializer
)
from .permissions import (
    IsClient,
    IsProvider,
    IsAdmin,
    IsOwnerOrAdmin,
    IsOwnerOrReadOnly,
    IsClientOrProviderOrAdmin,
    IsAuthenticatedAndActive
)

# Create your views here.

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """فقط اطلاعات کاربر جاری را برمی‌گرداند مگر اینکه ادمین باشد"""
        if self.request.user.is_admin:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=self.request.user.id)

class ClientProfileViewSet(viewsets.ModelViewSet):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [IsClient | IsAdmin]

    def get_queryset(self):
        """فقط پروفایل کاربر جاری را برمی‌گرداند مگر اینکه ادمین باشد"""
        if self.request.user.is_admin:
            return ClientProfile.objects.all()
        return ClientProfile.objects.filter(user=self.request.user)

class ProviderProfileViewSet(viewsets.ModelViewSet):
    queryset = ProviderProfile.objects.all()
    serializer_class = ProviderProfileSerializer
    permission_classes = [IsProvider | IsAdmin]

    def get_queryset(self):
        """فقط پروفایل کاربر جاری را برمی‌گرداند مگر اینکه ادمین باشد"""
        if self.request.user.is_admin:
            return ProviderProfile.objects.all()
        return ProviderProfile.objects.filter(user=self.request.user)

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        """فقط آدرس‌های کاربر جاری را برمی‌گرداند مگر اینکه ادمین باشد"""
        if self.request.user.is_admin:
            return Address.objects.all()
        return Address.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """تنظیم آدرس به عنوان پیش‌فرض"""
        address = self.get_object()
        if address.user != request.user and not request.user.is_admin:
            return Response(
                {"error": "شما اجازه تغییر این آدرس را ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # غیرفعال کردن آدرس پیش‌فرض قبلی
        Address.objects.filter(user=address.user, is_default=True).update(is_default=False)
        
        # تنظیم آدرس جدید به عنوان پیش‌فرض
        address.is_default = True
        address.save()
        
        return Response(
            {"message": "آدرس با موفقیت به عنوان پیش‌فرض تنظیم شد"},
            status=status.HTTP_200_OK
        )

class AuthViewSet(viewsets.ViewSet):
    permission_classes = []  # اجازه دسترسی به همه

    @action(detail=False, methods=['post'])
    def register(self, request):
        """ثبت‌نام کاربر جدید"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "ثبت‌نام با موفقیت انجام شد"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """ورود کاربر"""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user and user.is_active:
                login(request, user)
                return Response({"message": "ورود موفقیت‌آمیز بود"})
            return Response(
                {"error": "نام کاربری یا رمز عبور اشتباه است"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedAndActive])
    def logout(self, request):
        """خروج کاربر"""
        logout(request)
        return Response({"message": "خروج موفقیت‌آمیز بود"})

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedAndActive])
    def change_password(self, request):
        """تغییر رمز عبور"""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.validated_data['old_password']):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"message": "رمز عبور با موفقیت تغییر کرد"})
            return Response(
                {"error": "رمز عبور فعلی اشتباه است"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
