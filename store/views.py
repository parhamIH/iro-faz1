from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from .filters import *
# from loan_calculator.models import LoanCondition, PrePaymentInstallment
# from loan_calculator.serializers import LoanConditionSerializer, PrePaymentInstallmentSerializer
from django.http import Http404, JsonResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.db.models import Count, Q
from django.utils import timezone

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class BaseModelViewSet(ModelViewSet):
    pagination_class = StandardResultsSetPagination

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup = self.kwargs[lookup_url_kwarg]

        if lookup.isdigit():
            try:
                obj = queryset.get(id=lookup)
                self.check_object_permissions(self.request, obj)
                return obj
            except self.queryset.model.DoesNotExist:
                pass

        if hasattr(self.queryset.model, 'slug'):
            try:
                obj = queryset.get(slug=lookup)
                self.check_object_permissions(self.request, obj)
                return obj
            except self.queryset.model.DoesNotExist:
                pass

        raise Http404

    def list(self, request, *args, **kwargs):
        try:
            parent_id = request.GET.get('parent')
            if parent_id:
                # اگر پارامتر parent وجود داشت، خود parent را هم به عنوان اولین عضو لیست برگردان
                try:
                    parent_obj = Category.objects.prefetch_related('products', 'spec_definitions').select_related('parent').get(id=parent_id)
                    parent_data = self.get_serializer(parent_obj).data
                except Category.DoesNotExist:
                    parent_data = None
                queryset = self.filter_queryset(self.get_queryset())
                page = self.paginate_queryset(queryset)
                filter_instance = CategoryFilter(request.GET, queryset=Category.objects.all(), request=request)
                filters_data = {}
                for name, f in filter_instance.filters.items():
                    filters_data[name] = {
                        'label': getattr(f, 'label', name),
                        'help_text': getattr(f, 'help_text', ''),
                        'choices': getattr(f, 'choices', None),
                    }
                filters_data['spec_value_choices'] = filter_instance.spec_value_choices
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    data = list(serializer.data)
                    if parent_data:
                        data.insert(0, parent_data)
                    response = self.get_paginated_response(data)
                    response.data['status'] = 'success'
                    response.data['filters'] = filters_data
                    return response
                serializer = self.get_serializer(queryset, many=True)
                data = list(serializer.data)
                if parent_data:
                    data.insert(0, parent_data)
                return Response({
                    'status': 'success',
                    'data': data,
                    'filters': filters_data
                })
            # حالت عادی (بدون parent)
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            filter_instance = CategoryFilter(request.GET, queryset=Category.objects.all(), request=request)
            filters_data = {}
            for name, f in filter_instance.filters.items():
                filters_data[name] = {
                    'label': getattr(f, 'label', name),
                    'help_text': getattr(f, 'help_text', ''),
                    'choices': getattr(f, 'choices', None),
                }
            filters_data['spec_value_choices'] = filter_instance.spec_value_choices
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                response.data['status'] = 'success'
                response.data['filters'] = filters_data
                return response
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'data': serializer.data,
                'filters': filters_data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProductViewSet(BaseModelViewSet):
    queryset = Product.objects.prefetch_related(
        'tags',
        'categories', 'brand', 'options',
        'options__color', 'spec_values',
        'spec_values__specification'
    ).all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    ordering_fields = ['options__option_price','options__quantity', "created_at" , "updated_at" , "is_active" , "options__is_active_discount"]
    search_fields = ['title', 'description','options__color__name','options__option_price']

class CategoryViewSet(BaseModelViewSet):
    queryset = Category.objects.prefetch_related('products', 'spec_definitions', 'brand').select_related('parent').all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name',]
    ordering = ['name']

    @action(detail=True, methods=['get'], url_path='specifications')
    def specifications(self, request, pk=None):
        """
        لیست مشخصات فنی این دسته‌بندی به همراه مقادیر یکتای هر مشخصه (بر اساس محصولات این دسته‌بندی)
        خروجی مناسب برای ساخت فیلتر داینامیک در فرانت‌اند
        """
        category = self.get_object()
        serializer = CategorySpecificationWithValuesSerializer(category)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='filter-metadata')
    def filter_metadata(self, request, pk=None):
        """
        متادیتا و لیست فیلترهای قابل استفاده برای این دسته‌بندی (شامل choices داینامیک مشخصات فنی)
        """
        category = self.get_object()
        # فیلتر را با context مناسب بساز
        filter_instance = CategoryFilter(request.GET, queryset=Category.objects.all(), request=request)
        filters_data = {}
        for name, f in filter_instance.filters.items():
            filters_data[name] = {
                'label': getattr(f, 'label', name),
                'help_text': getattr(f, 'help_text', ''),
                'choices': getattr(f, 'choices', None),
            }
        # اضافه کردن choices داینامیک برای spec_value
        filters_data['spec_value_choices'] = filter_instance.spec_value_choices
        return Response(filters_data)

class BrandViewSet(BaseModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class ProductOptionViewSet(BaseModelViewSet):
    queryset = ProductOption.objects.select_related('product', 'color').all()
    serializer_class = ProductOptionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'color', 'is_active', 'is_active_discount']
    search_fields = ['product__title']
    ordering_fields = ['option_price', 'quantity']
    ordering = ['-is_active', 'option_price']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            # فقط محصولات فعال در لیست نمایش داده شوند
            return queryset.filter(is_active=True)
        return queryset

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

# class LoanConditionViewSet(BaseModelViewSet):
#     queryset = LoanCondition.objects.all()
#     serializer_class = LoanConditionSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     filterset_fields = ['condition_type', 'product']
#     search_fields = ['title', 'product__title']

# class PrePaymentInstallmentViewSet(BaseModelViewSet):
#     queryset = PrePaymentInstallment.objects.all()
#     serializer_class = PrePaymentInstallmentSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     filterset_fields = ['loan_condition']
#     search_fields = ['loan_condition__title']

class SpecificationViewSet(BaseModelViewSet):
    queryset = Specification.objects.select_related('category').all()
    serializer_class = SpecificationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SpecificationFilter
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'data_type']
    ordering = ['name']

class ProductSpecificationViewSet(BaseModelViewSet):
    queryset = ProductSpecification.objects.all()
    serializer_class = ProductSpecificationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'specification']
    search_fields = ['specification__name', 'product__title']



class WarrantyViewSet(BaseModelViewSet):
    queryset = Warranty.objects.all()
    serializer_class = WarrantySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product_options']
    search_fields = ['product_options__product__title']


class TagViewSet(BaseModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    filterset_fields = ['name']
