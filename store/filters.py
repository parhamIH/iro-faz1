from django_filters import FilterSet, RangeFilter, CharFilter, BooleanFilter, ChoiceFilter, NumberFilter, Filter
from django.db.models import Q
from .models import Category, Product, Brand, Color, Specification, Tag, SpecificationGroup, Warranty, ProductOption

class CommaSeparatedModelMultipleChoiceFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', None)
        self.field_name = kwargs.get('field_name')
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs
        
        # اگر متد سفارشی تعریف شده، آن را فراخوانی کن
        if hasattr(self, 'method') and self.method:
            return getattr(self.parent, self.method)(qs, self.field_name, value)
        
        # در غیر این صورت، پارس کردن معمولی
        if isinstance(value, str):
            value = [v.strip() for v in value.split(',') if v.strip()]
        try:
            value = [int(v) for v in value]
        except Exception:
            return qs.none()
        return qs.filter(**{f"{self.field_name}__in": value})

# --- SpecificationFilter ---
class SpecificationFilter(FilterSet):
    """
    فیلتر مشخصات فنی برای بخش مدیریت یا پنل
    """
    search = CharFilter(method='filter_search', label='جستجو')
    categories = CommaSeparatedModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.all(),
        label='دسته‌بندی‌ها',
        method='filter_categories_with_children',
    )
    group = CommaSeparatedModelMultipleChoiceFilter(
        field_name='group',
        queryset=SpecificationGroup.objects.all(),
        label='گروه‌های مشخصات'
    )
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(unit__icontains=value) |
            Q(categories__name__icontains=value) |
            Q(categories__parent__name__icontains=value) |
            Q(group__name__icontains=value)
        ).distinct()
    
    def filter_categories(self, queryset, name, value):
        if not value:
            return queryset
        all_ids = set()
        for cat in value:
            all_ids.add(cat.id)
            all_ids.update(cat.get_descendants().values_list('id', flat=True))
        return queryset.filter(categories__in=all_ids).distinct()

    class Meta:
        model = Specification
        fields = {
            'categories': ['exact'],
            'group': ['exact'],
            'data_type': ['exact'],
            'name': ['exact', 'icontains'],
            "is_main": ['exact'],
            "unit": ['exact', 'icontains'],
        }

# --- SpecificationGroupFilter ---
class SpecificationGroupFilter(FilterSet):
    """
    فیلتر گروه‌های مشخصات
    """
    search = CharFilter(method='filter_search', label='جستجو')
    has_specifications = BooleanFilter(method='filter_has_specifications', label='دارای مشخصات')
    
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(specifications__name__icontains=value)
        ).distinct()
    
    def filter_has_specifications(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(specifications__isnull=False).distinct()
        return queryset.filter(specifications__isnull=True).distinct()

    class Meta:
        model = SpecificationGroup
        fields = {
            'name': ['exact', 'icontains'],
        }

# --- WarrantyFilter ---
class WarrantyFilter(FilterSet):
    """
    فیلتر گارانتی‌ها
    """
    search = CharFilter(method='filter_search', label='جستجو')
    duration_range = RangeFilter(field_name='duration', label='محدوده مدت گارانتی')
    has_product_options = BooleanFilter(method='filter_has_product_options', label='دارای محصول')
    
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(company__icontains=value) |
            Q(description__icontains=value)
        ).distinct()
    
    def filter_has_product_options(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(product_options__isnull=False).distinct()
        return queryset.filter(product_options__isnull=True).distinct()

    class Meta:
        model = Warranty
        fields = {
            'name': ['exact', 'icontains'],
            'company': ['exact', 'icontains'],
            'is_active': ['exact'],
            'duration': ['exact', 'gte', 'lte'],
            'registration_required': ['exact'],
        }

# --- ProductOptionFilter ---
class ProductOptionFilter(FilterSet):
    """
    فیلتر ویژگی‌های محصول
    """
    search = CharFilter(method='filter_search', label='جستجو')
    price_range = RangeFilter(field_name='option_price', label='محدوده قیمت')
    discount_range = RangeFilter(field_name='discount', label='محدوده تخفیف')
    has_warranty = BooleanFilter(method='filter_has_warranty', label='دارای گارانتی')
    has_discount = BooleanFilter(method='filter_has_discount', label='دارای تخفیف')
    
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(product__title__icontains=value) |
            Q(color__name__icontains=value) |
            Q(warranty__name__icontains=value)
        ).distinct()
    
    def filter_has_warranty(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(warranty__isnull=False).distinct()
        return queryset.filter(warranty__isnull=True).distinct()
    
    def filter_has_discount(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(is_active_discount=True, discount__gt=0).distinct()
        return queryset.filter(Q(is_active_discount=False) | Q(discount=0)).distinct()

    class Meta:
        model = ProductOption
        fields = {
            'product': ['exact'],
            'color': ['exact'],
            'warranty': ['exact'],
            'is_active': ['exact'],
            'is_active_discount': ['exact'],
            'option_price': ['exact', 'gte', 'lte'],
            'quantity': ['exact', 'gte', 'lte'],
            'discount': ['exact', 'gte', 'lte'],
        }

# --- ProductFilter ---
class ProductFilter(FilterSet):
    search = CharFilter(method='filter_search', label='جستجو')
    in_stock = BooleanFilter(method='filter_in_stock', label='موجودی')
    price_range = RangeFilter(field_name='options__option_price', label='محدوده قیمت')
    has_discount = BooleanFilter(method='filter_has_discount', label='دارای تخفیف')
    has_warranty = BooleanFilter(method='filter_has_warranty', label='دارای گارانتی')
    tags = CommaSeparatedModelMultipleChoiceFilter(
        field_name='tags',
        queryset=Tag.objects.all(),
        label='تگ‌ها',
    )
    brands = CommaSeparatedModelMultipleChoiceFilter(
        field_name='brand',
        queryset=Brand.objects.all(),
        label='برندها',
    )
    colors = CommaSeparatedModelMultipleChoiceFilter(
        field_name='options__color',
        queryset=Color.objects.all(),
        label='رنگ‌ها',
    )
    categories = CharFilter(method='filter_categories_with_children', label='دسته‌بندی‌ها')
    category_title = CharFilter(method='filter_categories_by_slug', label='دسته‌بندی‌ها (با slug)')
    warranties = CommaSeparatedModelMultipleChoiceFilter(
        field_name='options__warranty',
        queryset=Warranty.objects.all(),
        label='گارانتی‌ها',
    )
    spec_groups = CommaSeparatedModelMultipleChoiceFilter(
        field_name='spec_values__specification__group',
        queryset=SpecificationGroup.objects.all(),
        label='گروه‌های مشخصات',
    )
    specification = CharFilter(method='filter_specification', label='مشخصات فنی')
    spec_value = CharFilter(method='filter_specification', label='مقدار مشخصه (نام:مقدار)')
    spec_by_id = CharFilter(method='filter_specification_by_id', label='مشخصات فنی (آیدی مقدار)')
    spec_ids = CommaSeparatedModelMultipleChoiceFilter(
        field_name='spec_values__specification',
        queryset=Specification.objects.all(),
        label='مشخصات فنی (آیدی)',
    )
    spec_value_ids = CommaSeparatedModelMultipleChoiceFilter(
        field_name='spec_values',
        queryset=None,
        label='مقادیر مشخصات فنی (آیدی)',
        method='filter_spec_value_ids',
    )
    

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(brand__name__icontains=value) |
            Q(categories__name__icontains=value) |
            Q(spec_values__specification__name__icontains=value)
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
    
    def filter_has_warranty(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(options__warranty__isnull=False).distinct()
        return queryset.filter(options__warranty__isnull=True).distinct()

    def filter_categories_with_children(self, queryset, name, value):
        if not value:
            return queryset
        # اگر مقدار رشته بود، به لیست آیدی تبدیل کن
        if isinstance(value, str):
            value = [v.strip() for v in value.split(',') if v.strip()]
            try:
                value = [int(v) for v in value]
            except Exception:
                return queryset.none()
        all_category_ids = set()
        for category_id in value:
            try:
                category = Category.objects.get(id=category_id)
                all_category_ids.add(category.id)
                descendants = category.get_descendants()
                all_category_ids.update(descendants.values_list('id', flat=True))
            except Category.DoesNotExist:
                continue
        return queryset.filter(categories__id__in=all_category_ids).distinct()

    def filter_categories_by_slug(self, queryset, name, value):
        """
        فیلتر محصولات بر اساس slug دسته‌بندی‌ها
        فرمت ورودی: "laptop,phone,tablet" یا "laptop"
        مثال: "laptop,phone" - محصولاتی که در دسته‌بندی‌های laptop یا phone هستند
        """
        if not value:
            return queryset
        
        # تبدیل رشته به لیست slug ها
        if isinstance(value, str):
            slugs = [slug.strip() for slug in value.split(',') if slug.strip()]
        else:
            slugs = value
        
        # پیدا کردن دسته‌بندی‌ها بر اساس slug
        categories = Category.objects.filter(slug__in=slugs)
        if not categories.exists():
            return queryset.none()
        
        # جمع‌آوری همه آیدی‌های دسته‌بندی و زیرمجموعه‌های آن‌ها
        all_category_ids = set()
        for category in categories:
            all_category_ids.add(category.id)
            # اضافه کردن زیرمجموعه‌ها (descendants)
            descendants = category.get_descendants()
            all_category_ids.update(descendants.values_list('id', flat=True))
        
        return queryset.filter(categories__id__in=all_category_ids).distinct()

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
    
    def filter_specification_by_id(self, queryset, name, value):
        """
        فیلتر محصولات بر اساس آیدی مقدار مشخصات فنی (ProductSpecification)
        فرمت ورودی: "128" یا "128,512,700"
        مثال: "128,512"
        همه value idها با ویرگول جدا می‌شوند و فیلتر OR است.
        """
        if not value:
            return queryset
        value_ids = [v.strip() for v in value.split(',') if v.strip()]
        try:
            value_ids = [int(v) for v in value_ids]
        except Exception:
            return queryset.none()
        return queryset.filter(spec_values__id__in=value_ids).distinct()

    def filter_spec_value_ids(self, queryset, field_name, value):
        """فیلتر کردن محصولات بر اساس آیدی مقادیر مشخصات فنی"""
        if not value:
            return queryset
        
        # تبدیل رشته به لیست آیدی‌ها
        if isinstance(value, str):
            value = [v.strip() for v in value.split(',') if v.strip()]
        
        try:
            value_ids = [int(v) for v in value]
        except (ValueError, TypeError):
            return queryset.none()
        
        # فیلتر کردن محصولاتی که دارای این مقادیر مشخصات فنی هستند
        return queryset.filter(spec_values__id__in=value_ids).distinct()

    class Meta:
        model = Product
        fields = {
            'is_active': ['exact'],
        }

# --- CategoryFilter ---
class CategoryFilter(FilterSet):
    search = CharFilter(method='filter_search', label='جستجو')
    has_products = BooleanFilter(method='filter_has_products', label='دارای محصول')
    has_specifications = BooleanFilter(method='filter_has_specifications', label='دارای مشخصات')
    brands = CommaSeparatedModelMultipleChoiceFilter(
        field_name='brand',
        queryset=Brand.objects.all(),
        label='برندها',
    )
    spec_group = CommaSeparatedModelMultipleChoiceFilter(
        field_name='spec_definitions__group',
        queryset=SpecificationGroup.objects.all(),
        label='گروه مشخصات',
    )
    spec_definitions = CommaSeparatedModelMultipleChoiceFilter(
        field_name='spec_definitions',
        queryset=Specification.objects.all(),
        label='مشخصات فنی (آیدی)',
        help_text='مشخصات فنی را انتخاب کنید',
    )
    spec_names = CharFilter(field_name='spec_definitions__name', lookup_expr='icontains', label='مشخصات فنی (نام)')
    
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
    
    # فیلتر ترکیبی برای مقدار مشخصه فقط با آیدی مشخصه و مقدار هم آیدی مقدار مشخصه محصول (پشتیبانی از چند کلید و چند مقدار با جداکننده _)
    spec_value = CharFilter(method='filter_spec_value', label='مقدار مشخصه (آیدی مقدار)', help_text='فرمت: value_id1,value_id2,...')
    
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(brand__name__icontains=value) |
            Q(spec_definitions__name__icontains=value)
        ).distinct()

    def filter_has_products(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(products__isnull=False).distinct()
        return queryset.filter(products__isnull=True).distinct()
    
    def filter_has_specifications(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(spec_definitions__isnull=False).distinct()
        return queryset.filter(spec_definitions__isnull=True).distinct()

    def filter_spec_value(self, queryset, name, value):
        """
        فیلتر بر اساس مقدار مشخصه فنی فقط با آیدی مقدار مشخصه محصول (ProductSpecification)
        فرمت:
        - "151"
        - "151,152,153"
        مثال: "151,152,153"
        همه value idها با ویرگول جدا می‌شوند و فیلتر OR است.
        """
        if not value:
            return queryset
        value_ids = [v.strip() for v in value.split(',') if v.strip()]
        try:
            value_ids = [int(v) for v in value_ids]
        except Exception:
            return queryset.none()
        return queryset.filter(products__spec_values__id__in=value_ids).distinct()

    class Meta:
        model = Category
        fields = {
            'name': ['exact', 'icontains'],
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


