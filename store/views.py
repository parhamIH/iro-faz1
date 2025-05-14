from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category, InstallmentPlan, Discount, Brand
from .serializers import (
    ProductSerializer, CategorySerializer, InstallmentPlanSerializer,
    DiscountSerializer, BrandSerializer
)
from django.http import Http404

class BaseModelViewSet(viewsets.ModelViewSet):
    """
    پایه برای همه ViewSetها با پشتیبانی از ID و Slug
    """
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup = self.kwargs[lookup_url_kwarg]
        
        # اول با ID تلاش می‌کنیم
        if lookup.isdigit():
            try:
                obj = queryset.get(id=lookup)
                self.check_object_permissions(self.request, obj)
                return obj
            except self.queryset.model.DoesNotExist:
                pass
        
        # اگر ID نبود یا پیدا نشد، با slug تلاش می‌کنیم
        if hasattr(self.queryset.model, 'slug'):
            try:
                obj = queryset.get(slug=lookup)
                self.check_object_permissions(self.request, obj)
                return obj
            except self.queryset.model.DoesNotExist:
                pass
        
        raise Http404

class ProductViewSet(BaseModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categories', 'brand']
    search_fields = ['title', 'description', 'brand__name', 'categories__name']
    ordering_fields = ['title', 'base_price_cash']
    ordering = ['title']

class CategoryViewSet(BaseModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class InstallmentPlanViewSet(BaseModelViewSet):
    queryset = InstallmentPlan.objects.all()
    serializer_class = InstallmentPlanSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['months', 'product']

class DiscountViewSet(BaseModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['percentage']
    search_fields = ['name']

class BrandViewSet(BaseModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
