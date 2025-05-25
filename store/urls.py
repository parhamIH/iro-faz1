from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, BrandViewSet,
    ProductOptionViewSet, ColorViewSet,
    SpecificationViewSet, ProductSpecificationViewSet, WarrantyViewSet
)
# لیست همه محصولات: http://localhost:8000/api/products/
# یک محصول خاص: http://localhost:8000/api/products/[slug-محصول]/

# ساخت یک روتر پیش‌فرض برای مسیریابی خودکار
router = DefaultRouter()

# Register viewsets with clean URL patterns
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('brands', BrandViewSet)
router.register('product-options', ProductOptionViewSet)
router.register('colors', ColorViewSet)
router.register('specifications', SpecificationViewSet)
router.register('product-specifications', ProductSpecificationViewSet)
router.register('warranties', WarrantyViewSet)
# الگوهای URL
urlpatterns = [
    # اضافه کردن تمام مسیرهای روتر به برنامه
    path('', include(router.urls)),
]
