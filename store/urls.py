from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductListView, ProductDetailView,
    categoriesView, CategoryView,
    InstallmentPlanViewSet, DiscountViewSet
)

router = DefaultRouter()
router.register(r'installment-plans', InstallmentPlanViewSet, basename='installmentplan')
router.register(r'discounts', DiscountViewSet)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', categoriesView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryView.as_view(), name='category-detail'),
    path('', include(router.urls)),
]
