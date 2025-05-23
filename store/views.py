from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Product, Category, Brand, Feature, ProductOption, 
    Color, Gallery, Specification, ProductSpecification
)
from loan_calculator.models import LoanCondition, PrePaymentInstallment
from .serializers import (
    ProductSerializer, CategorySerializer, BrandSerializer,
    FeatureSerializer, ProductOptionSerializer, ColorSerializer,
    GallerySerializer, SpecificationSerializer, ProductSpecificationSerializer
)
from loan_calculator.serializers import LoanConditionSerializer, PrePaymentInstallmentSerializer
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
    filterset_fields = ['categories', 'brand', 'is_active']
    search_fields = ['title', 'description', 'brand__name', 'categories__name']
    ordering_fields = ['title']
    ordering = ['title']

class CategoryViewSet(BaseModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class BrandViewSet(BaseModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class FeatureViewSet(BaseModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_main_feature']
    search_fields = ['name', 'value']

class ProductOptionViewSet(BaseModelViewSet):
    queryset = ProductOption.objects.all()
    serializer_class = ProductOptionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'color', 'is_active', 'is_active_discount']
    search_fields = ['product__title']

class ColorViewSet(BaseModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'hex_code']

class GalleryViewSet(BaseModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']

class LoanConditionViewSet(BaseModelViewSet):
    queryset = LoanCondition.objects.all()
    serializer_class = LoanConditionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['condition_type', 'product']
    search_fields = ['title', 'product__title']

class PrePaymentInstallmentViewSet(BaseModelViewSet):
    queryset = PrePaymentInstallment.objects.all()
    serializer_class = PrePaymentInstallmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['loan_condition']
    search_fields = ['loan_condition__title']

class SpecificationViewSet(BaseModelViewSet):
    queryset = Specification.objects.all()
    serializer_class = SpecificationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'data_type']
    search_fields = ['name', 'slug']

class ProductSpecificationViewSet(BaseModelViewSet):
    queryset = ProductSpecification.objects.all()
    serializer_class = ProductSpecificationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'specification']
    search_fields = ['specification__name', 'product__title']


