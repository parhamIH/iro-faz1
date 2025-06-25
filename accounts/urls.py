from django.urls import path
from .views import ChangePasswordView, ResetPasswordRequestView, ResetPasswordConfirmView , LoginView,RegisterView

urlpatterns = [
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/reset-password/request/', ResetPasswordRequestView.as_view(), name='reset-password-request'),
    path('auth/reset-password/confirm/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
]          