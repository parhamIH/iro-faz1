
from rest_framework import permissions

"""
کلاس‌های مجوز (Permission) برای کنترل دسترسی کاربران به API ها
هر کلاس یک سطح دسترسی خاص را تعریف می‌کند
"""

class IsAdmin(permissions.BasePermission):
    """
    مجوز برای دسترسی مدیران سیستم (Admin)
    شرایط لازم:
    - کاربر لاگین کرده باشد (is_authenticated)
    - کاربر عضو کارکنان باشد (is_staff)
    - کاربر ادمین کل سیستم باشد (is_superuser)
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.is_staff and request.user.is_superuser)

class IsProvider(permissions.BasePermission):
    """
    مجوز برای دسترسی ارائه‌دهندگان خدمات (Provider)
    شرایط لازم:
    - کاربر لاگین کرده باشد (is_authenticated)
    - کاربر عضو کارکنان باشد (is_staff)
    - کاربر ادمین کل نباشد (not is_superuser)
    - کاربر دارای پروفایل ارائه‌دهنده باشد (hasattr(user, 'provider'))
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.is_staff and not request.user.is_superuser and
                   hasattr(request.user, 'provider'))

class IsAdminOrProvider(permissions.BasePermission):
    """
    مجوز برای دسترسی هر دو گروه مدیران و ارائه‌دهندگان
    شرایط لازم:
    - کاربر لاگین کرده باشد (is_authenticated)
    - کاربر عضو کارکنان باشد (is_staff)
    این مجوز برای صفحاتی استفاده می‌شود که هر دو گروه باید به آن دسترسی داشته باشند
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff) 
