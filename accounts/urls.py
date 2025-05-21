from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('users', views.CustomUserViewSet)
router.register('clients', views.ClientProfileViewSet)
router.register('providers', views.ProviderProfileViewSet)
router.register('addresses', views.AddressViewSet)
router.register('auth', views.AuthViewSet, basename='auth')

app_name = 'accounts'

urlpatterns = [
    path('', include(router.urls)),
] 