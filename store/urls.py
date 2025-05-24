from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, BrandViewSet,
    FeatureViewSet, ProductOptionViewSet, ColorViewSet,
    GalleryViewSet, test_filters
)
# لیست همه محصولات: http://localhost:8000/api/products/
# یک محصول خاص: http://localhost:8000/api/products/[slug-محصول]/

# ساخت یک روتر پیش‌فرض برای مسیریابی خودکار
router = DefaultRouter()

# Register viewsets with clean URL patterns
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('brands', BrandViewSet)
router.register('features', FeatureViewSet)
router.register('options', ProductOptionViewSet)
router.register('colors', ColorViewSet)
router.register('gallery', GalleryViewSet)

# الگوهای URL
urlpatterns = [
    # اضافه کردن تمام مسیرهای روتر به برنامه
    path('', include(router.urls)),
    path('test-filters/', test_filters, name='test_filters'),
]
