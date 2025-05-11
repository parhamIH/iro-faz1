from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoanCalculatorViewSet

router = DefaultRouter()
router.register(r'calculator', LoanCalculatorViewSet, basename='loancalculator')

urlpatterns = [
    path('', include(router.urls)),
] 