
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ProductViewSet, CategoryViewSet, InstallmentPlanViewSet, DiscountViewSet)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'installment-plans', InstallmentPlanViewSet)
router.register(r'discounts', DiscountViewSet)

urlpatterns = [
    path('', include(router.urls)),  # اینجا نباید api/ دوباره استفاده بشه
]
