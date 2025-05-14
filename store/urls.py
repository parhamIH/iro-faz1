from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, InstallmentPlanViewSet,
    DiscountViewSet, BrandViewSet
)
# لیست همه محصولات: http://localhost:8000/api/products/
# یک محصول خاص: http://localhost:8000/api/products/[slug-محصول]/

# ساخت یک روتر پیش‌فرض برای مسیریابی خودکار
router = DefaultRouter()

# Register viewsets with clean URL patterns
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('installments', InstallmentPlanViewSet)
router.register('discounts', DiscountViewSet)
router.register('brands', BrandViewSet)

# الگوهای URL
urlpatterns = [
    # اضافه کردن تمام مسیرهای روتر به برنامه
    path('', include(router.urls)),
]
