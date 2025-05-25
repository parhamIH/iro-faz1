from django_filters import FilterSet, RangeFilter, CharFilter, BooleanFilter, ChoiceFilter, NumberFilter, ModelMultipleChoiceFilter
from django.db.models import Q
from .models import Category, Product, Brand, Color, Specification, Tag

class SpecificationFilter(FilterSet):
    """
    فیلتر مشخصات فنی برای بخش مدیریت یا پنل
    """
    search = CharFilter(method='filter_search', label='جستجو')
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value)
        ).distinct()
    
    class Meta:
        model = Specification
        fields = {
            'category': ['exact'],
            'data_type': ['exact'],
            'name': ['exact', 'icontains'],
        }

class ProductFilter(FilterSet):
    search = CharFilter(method='filter_search', label='جستجو')
    in_stock = BooleanFilter(method='filter_in_stock', label='موجودی')
    price_range = RangeFilter(field_name='options__option_price', label='محدوده قیمت')
    has_discount = BooleanFilter(method='filter_has_discount', label='دارای تخفیف')
    tags = ModelMultipleChoiceFilter(
        field_name='tags',
        queryset=Tag.objects.all(),
        label='تگ‌ها',
        help_text='تگ‌هایی که با این محصول مرتبط هستند',
        method='filter_tags'
    )


    brands = ModelMultipleChoiceFilter(
        field_name='brand',
        queryset=Brand.objects.all(),
        label='برندها'
    )
    colors = ModelMultipleChoiceFilter(
        field_name='options__color',
        queryset=Color.objects.all(),
        distinct=True,
        label='رنگ‌ها'
    )
    categories = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.all(),
        label='دسته‌بندی‌ها'
    )

    specification = CharFilter(method='filter_specification', label='مشخصات فنی')
    


    def filter_tags(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(tags__name__in=value).distinct()



    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(brand__name__icontains=value) |
            Q(categories__name__icontains=value)
        ).distinct()
    
    def filter_in_stock(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(options__quantity__gt=0, options__is_active=True).distinct()
        return queryset.filter(options__quantity=0).distinct()
    
    def filter_has_discount(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(
                options__is_active_discount=True,
                options__discount__gt=0
            ).distinct()
        return queryset.filter(
            Q(options__is_active_discount=False) |
            Q(options__discount=0)
        ).distinct()

    def filter_specification(self, queryset, name, value):
        if not value or ':' not in value:
            return queryset
            
        parts = value.split(':')
        spec_name = parts[0]
        
        if len(parts) == 2:
            return self._filter_spec_exact(queryset, spec_name, parts[1])
        elif len(parts) == 3:
            try:
                min_val = float(parts[1]) if parts[1] else None
                max_val = float(parts[2]) if parts[2] else None
                return self._filter_spec_range(queryset, spec_name, min_val, max_val)
            except ValueError:
                return queryset
        return queryset
    
    def _filter_spec_exact(self, queryset, name, value):
        q = Q(spec_values__specification__name__iexact=name)
        try:
            val = float(value)
            return queryset.filter(
                q & (Q(spec_values__int_value=val) | Q(spec_values__decimal_value=val))
            ).distinct()
        except ValueError:
            if value.lower() in ['true', 'false']:
                return queryset.filter(
                    q & Q(spec_values__bool_value=(value.lower() == 'true'))
                ).distinct()
            return queryset.filter(
                q & Q(spec_values__str_value__icontains=value)
            ).distinct()
    
    def _filter_spec_range(self, queryset, name, min_val, max_val):
        q = Q(spec_values__specification__name__iexact=name)
        if min_val is not None:
            q &= Q(spec_values__int_value__gte=min_val) | Q(spec_values__decimal_value__gte=min_val)
        if max_val is not None:
            q &= Q(spec_values__int_value__lte=max_val) | Q(spec_values__decimal_value__lte=max_val)
        return queryset.filter(q).distinct()

    class Meta:
        model = Product
        fields = ['is_active']


class CategoryFilter(FilterSet):
    search = CharFilter(method='filter_search', label='جستجو')
    has_products = BooleanFilter(method='filter_has_products', label='دارای محصول')
    
    # فیلترهای مشخصات فنی
    spec_name = CharFilter(field_name='spec_definitions__name', lookup_expr='icontains', label='نام مشخصه')
    spec_data_type = ChoiceFilter(
        field_name='spec_definitions__data_type',
        choices=Specification.DATA_TYPE_CHOICES,
        label='نوع داده مشخصه'
    )
    
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        ).distinct()
    
    def filter_has_products(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(products__isnull=False).distinct()
        return queryset.filter(products__isnull=True).distinct()

    class Meta:
        model = Category
        fields = {
            'parent': ['exact', 'isnull'],
            'brand': ['exact'],
            'spec_definitions': ['exact', 'in'],
        }


