from rest_framework import permissions

class IsClient(permissions.BasePermission):
    """
    دسترسی فقط برای کاربران با نقش مشتری
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_client)

    def has_object_permission(self, request, view, obj):
        # اجازه دسترسی به شی فقط اگر متعلق به خود کاربر باشد
        return obj.user == request.user

class IsProvider(permissions.BasePermission):
    """
    دسترسی فقط برای کاربران با نقش تأمین‌کننده
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_provider)

    def has_object_permission(self, request, view, obj):
        # اجازه دسترسی به شی فقط اگر متعلق به خود کاربر باشد
        return obj.user == request.user

class IsAdmin(permissions.BasePermission):
    """
    دسترسی فقط برای کاربران با نقش ادمین
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)

    def has_object_permission(self, request, view, obj):
        # ادمین به همه اشیا دسترسی دارد
        return True

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    دسترسی برای مالک شی یا ادمین
    """
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (obj.user == request.user or request.user.is_admin)
        )

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    اجازه خواندن برای همه، ولی ویرایش فقط برای مالک
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class IsClientOrProviderOrAdmin(permissions.BasePermission):
    """
    دسترسی برای کاربران با نقش مشتری یا تأمین‌کننده یا ادمین
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_client or request.user.is_provider or request.user.is_admin)
        )

class IsAuthenticatedAndActive(permissions.BasePermission):
    """
    دسترسی فقط برای کاربران احراز هویت شده و فعال
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_active
        ) 