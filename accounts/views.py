from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Provider, Profile
from .permissions import IsAdmin, IsProvider, IsAdminOrProvider

"""
ویوهای مربوط به مدیریت کاربران، ادمین‌ها و ارائه‌دهندگان
هر ویو با توجه به سطح دسترسی تعریف شده، قابل استفاده خواهد بود
"""

class ProviderViewSet(viewsets.ModelViewSet):
    """
    ویوست مدیریت ارائه‌دهندگان
    این کلاس امکانات زیر را فراهم می‌کند:
    - لیست تمام ارائه‌دهندگان (GET)
    - جزئیات یک ارائه‌دهنده (GET)
    - ایجاد ارائه‌دهنده جدید (POST) - فقط ادمین
    - ویرایش اطلاعات ارائه‌دهنده (PUT/PATCH) - فقط ادمین
    - حذف ارائه‌دهنده (DELETE) - فقط ادمین
    """
    permission_classes = [IsAdminOrProvider]
    
    def get_permissions(self):
        """
        تعیین سطح دسترسی پویا بر اساس نوع درخواست:
        - برای عملیات‌های ایجاد، ویرایش و حذف: فقط ادمین
        - برای مشاهده: هم ادمین و هم ارائه‌دهنده
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdmin]
        return super().get_permissions()

@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_dashboard(request):
    """
    داشبورد مخصوص ادمین
    این ویو فقط برای کاربران ادمین قابل دسترسی است
    می‌تواند شامل اطلاعات مدیریتی و گزارش‌های کلی سیستم باشد
    """
    return Response({"message": "Welcome to Admin Dashboard"})

@api_view(['GET'])
@permission_classes([IsProvider])
def provider_dashboard(request):
    """
    داشبورد مخصوص ارائه‌دهندگان
    این ویو فقط برای کاربران ارائه‌دهنده قابل دسترسی است
    می‌تواند شامل اطلاعات مربوط به خدمات و عملکرد ارائه‌دهنده باشد
    """
    return Response({"message": "Welcome to Provider Dashboard"})

@api_view(['GET'])
@permission_classes([IsAdminOrProvider])
def staff_dashboard(request):
    """
    داشبورد مشترک
    این ویو برای هر دو گروه ادمین و ارائه‌دهنده قابل دسترسی است
    اطلاعات نمایش داده شده بر اساس نقش کاربر (ادمین یا ارائه‌دهنده) متفاوت خواهد بود
    """
    if request.user.is_superuser:
        role = "Admin"
    else:
        role = "Provider"
    return Response({"message": f"Welcome to Staff Dashboard. Your role is: {role}"})
