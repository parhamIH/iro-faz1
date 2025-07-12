from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

class SuperuserRequiredMiddleware:
    """Middleware to handle superuser-only access"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            if not request.user.is_authenticated:
                return redirect('admin:login')
            else:
                messages.error(request, "فقط مدیران سیستم می‌توانند به این بخش دسترسی داشته باشند.")
                return redirect('admin:index')
        return None 