from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Traditional authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('reset-password-request/', views.ResetPasswordRequestView.as_view(), name='reset_password_request'),
    path('reset-password-confirm/', views.ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    
    # JWT Authentication with SMS verification
    path('sms-verification-request/', views.SMSVerificationRequestView.as_view(), name='sms_verification_request'),
    path('jwt-login/', views.JWTLoginView.as_view(), name='jwt_login'),
    path('jwt-refresh/', views.JWTRefreshView.as_view(), name='jwt_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Device management
    path('devices/', views.UserDevicesView.as_view(), name='user_devices'),
    path('revoke-device/', views.RevokeDeviceView.as_view(), name='revoke_device'),
]