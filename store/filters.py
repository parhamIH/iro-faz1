from django_filters import FilterSet, RangeFilter, CharFilter, BooleanFilter, ChoiceFilter, NumberFilter, ModelMultipleChoiceFilter, Filter
from django.db.models import Q
from .models import Category, Product, Brand, Color, Specification, Tag

class CommaOrMultiValueFilter(Filter):
    def filter(self, qs, value):
        if value is not None:
            if isinstance(value, str):
                value = value.split(',')
            elif not isinstance(value, list):
                value = [value]
        return super().filter(qs, value)

class SpecificationFilter(FilterSet):
    """
    فیلتر مشخصات فنی برای بخش مدیریت یا پنل
    """
    search = CharFilter(method='filter_search', label='جستجو')
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(unit__icontains=value) |
            Q(category__name__icontains=value) |
            Q(category__parent__name__icontains=value) |
            Q(category__brand__name__icontains=value) |
            Q(category__brand__parent__name__icontains=value)
        ).distinct()
    
    class Meta:
        model = Specification
        fields = {
            'category': ['exact'],
            'data_type': ['exact'],
            'name': ['exact', 'icontains'],
            "is_main": ['exact'],
            "slug": ['exact', 'icontains'],
            "unit": ['exact', 'icontains'],
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
        """
        Filters products by technical specifications.
        Input format: "specification_name:value" or "specification_name:min:max" or "specification_name:value1,value2,value3"
        Examples: "RAM:8GB", "Storage:128:512", "Color:Black,White", "Bluetooth:true"
        Supports multiple values for the same specification using commas (OR logic).
        Multiple specification filters in the query string are combined with AND logic by django-filter.
        """
        if not value or ':' not in value:
            return queryset

        parts = value.split(':')
        spec_name = parts[0]

        if len(parts) == 2:
            # Handle exact match or multiple exact values
            values = parts[1].split(',')
            return self._filter_spec_values(queryset, spec_name, values)
        elif len(parts) == 3:
            # Handle range filter
            try:
                min_val = float(parts[1]) if parts[1] else None
                max_val = float(parts[2]) if parts[2] else None
                return self._filter_spec_range(queryset, spec_name, min_val, max_val)
            except ValueError:
                # Invalid range values
                return queryset
        # Invalid format
        return queryset

    def _filter_spec_values(self, queryset, name, values):
        """Filters queryset for a specification by a list of exact values (OR logic)."""
        if not values:
            return queryset

        spec_q = Q(spec_values__specification__name__iexact=name)
        value_q = Q()

        for value in values:
            value = value.strip()
            try:
                # Try filtering as number (int or decimal)
                num_val = float(value)
                value_q |= (Q(spec_values__int_value=num_val) | Q(spec_values__decimal_value=num_val))
            except ValueError:
                # Try filtering as boolean
                if value.lower() in ['true', 'false']:
                    value_q |= Q(spec_values__bool_value=(value.lower() == 'true'))
                else:
                    # Filter as string (case-insensitive contains)
                    value_q |= Q(spec_values__str_value__icontains=value)

        return queryset.filter(spec_q & value_q).distinct()

    def _filter_spec_range(self, queryset, name, min_val, max_val):
        """Filters queryset for a specification by a numeric range."""
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
    
    # فیلتر برای مشخصات فنی با ID - قابل انتخاب
    spec_definitions = ModelMultipleChoiceFilter(
        queryset=Specification.objects.all(),
        method='filter_spec_definitions',
        label='مشخصات فنی (آیدی)',
        help_text='مشخصات فنی را انتخاب کنید'
    )
    
    # فیلتر برای مشخصات فنی با نام - قابل انتخاب
    spec_names = ModelMultipleChoiceFilter(
        queryset=Specification.objects.all(),
        method='filter_spec_names',
        label='مشخصات فنی (نام)',
        help_text='نام مشخصات فنی را انتخاب کنید'
    )
    
    # فیلترهای مقادیر مشخصات فنی
    spec_int_value = NumberFilter(
        field_name='products__spec_values__int_value',
        lookup_expr='exact',
        label='مقدار عددی مشخصه'
    )
    
    spec_decimal_value = NumberFilter(
        field_name='products__spec_values__decimal_value',
        lookup_expr='exact',
        label='مقدار اعشاری مشخصه'
    )
    
    spec_str_value = CharFilter(
        field_name='products__spec_values__str_value',
        lookup_expr='icontains',
        label='مقدار متنی مشخصه'
    )
    
    spec_bool_value = BooleanFilter(
        field_name='products__spec_values__bool_value',
        label='مقدار بله/خیر مشخصه'
    )
    
    # فیلتر ترکیبی برای مقدار مشخصه با نام مشخصه
    spec_value = CharFilter(method='filter_spec_value', label='مقدار مشخصه (نام:مقدار)')
    
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

    def filter_spec_definitions(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(spec_definitions__in=value).distinct()

    def filter_spec_names(self, queryset, name, value):
        if not value:
            return queryset
        spec_names = [spec.name for spec in value]
        return queryset.filter(spec_definitions__name__in=spec_names).distinct()

    def filter_spec_value(self, queryset, name, value):
        if not value or ':' not in value:
            return queryset
        
        parts = value.split(':')
        spec_name = parts[0].strip()
        
        if len(parts) == 2:
            values = [v.strip() for v in parts[1].split(',')]
            q = Q()
            for val in values:
                # تلاش برای int
                try:
                    num_val = int(val)
                    q |= Q(products__spec_values__specification__name__iexact=spec_name,
                           products__spec_values__int_value=num_val)
                    continue
                except ValueError:
                    pass
                # تلاش برای float
                try:
                    num_val = float(val)
                    q |= Q(products__spec_values__specification__name__iexact=spec_name,
                           products__spec_values__decimal_value=num_val)
                    continue
                except ValueError:
                    pass
                # تلاش برای bool
                if val.lower() in ['true', 'false']:
                    q |= Q(products__spec_values__specification__name__iexact=spec_name,
                           products__spec_values__bool_value=(val.lower() == 'true'))
                else:
                    # متن
                    q |= Q(products__spec_values__specification__name__iexact=spec_name,
                           products__spec_values__str_value__icontains=val)
            return queryset.filter(q).distinct()
        return queryset

    class Meta:
        model = Category
        fields = {
            'parent': ['exact', 'isnull'],
            'brand': ['exact'],
        }

    @property
    def spec_value_choices(self):
        # فرض: category_id از context یا request گرفته می‌شود
        from .models import Category
        from .serializers import CategorySpecificationWithValuesSerializer
        request = getattr(self, 'request', None)
        category_id = None
        if request:
            category_id = request.query_params.get('id') or request.query_params.get('category')
        if not category_id:
            return []
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return []
        serializer = CategorySpecificationWithValuesSerializer(category)
        return serializer.data.get('specifications', [])


