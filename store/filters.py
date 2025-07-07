from django_filters import FilterSet, RangeFilter, CharFilter, BooleanFilter, ChoiceFilter, NumberFilter, ModelMultipleChoiceFilter
from django.db.models import Q
from .models import Category, Product, Brand, Color, Specification, Tag, Warranty

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
    # جستجو و فیلترهای پایه
    search = CharFilter(method='filter_search', label='جستجو')
    in_stock = BooleanFilter(method='filter_in_stock', label='موجود در انبار')
    price_range = RangeFilter(field_name='options__option_price', label='محدوده قیمت')
    has_discount = BooleanFilter(method='filter_has_discount', label='دارای تخفیف')
    
    # فیلترهای مرتب‌سازی (مثل تکنولایف)
    sort_by = ChoiceFilter(
        method='filter_sort_by',
        label='مرتب‌سازی',
        choices=[
            ('newest', 'جدیدترین'),
            ('bestselling', 'پرفروش‌ترین'),
            ('most_viewed', 'پربازدیدترین'),
            ('cheapest', 'ارزان‌ترین'),
            ('most_expensive', 'گران‌ترین'),
            ('most_discount', 'بیشترین تخفیف'),
            ('most_rated', 'بیشترین امتیاز')
        ]
    )

    # فیلترهای دسته‌بندی و برند
    categories = ModelMultipleChoiceFilter(
        field_name='categories',
        queryset=Category.objects.all(),
        label='دسته‌بندی‌ها'
    )
    brands = ModelMultipleChoiceFilter(
        field_name='brand',
        queryset=Brand.objects.all(),
        label='برندها'
    )

    # فیلترهای رنگ
    colors = ModelMultipleChoiceFilter(
        field_name='options__color',
        queryset=Color.objects.all(),
        distinct=True,
        label='رنگ‌ها'
    )

    # فیلترهای پیشرفته
    is_new = BooleanFilter(method='filter_is_new', label='کالاهای جدید')
    special_offer = BooleanFilter(method='filter_special_offer', label='پیشنهاد ویژه')
    min_rating = NumberFilter(method='filter_min_rating', label='حداقل امتیاز')
    tags = ModelMultipleChoiceFilter(
        field_name='tags',
        queryset=Tag.objects.all(),
        label='برچسب‌ها'
    )

    # فیلتر مشخصات فنی
    specification = CharFilter(method='filter_specification', label='مشخصات فنی')

    def filter_sort_by(self, queryset, name, value):
        if value == 'newest':
            return queryset.order_by('-created_at')
        elif value == 'bestselling':
            return queryset.order_by('-total_sales')
        elif value == 'most_viewed':
            return queryset.order_by('-views')
        elif value == 'cheapest':
            return queryset.order_by('options__option_price')
        elif value == 'most_expensive':
            return queryset.order_by('-options__option_price')
        elif value == 'most_discount':
            return queryset.filter(
                options__is_active_discount=True
            ).order_by('-options__discount')
        elif value == 'most_rated':
            return queryset.order_by('-rating')
        return queryset

    def filter_special_offer(self, queryset, name, value):
        if value:
            return queryset.filter(
                options__is_active_discount=True,
                options__discount__gte=30  # پیشنهاد ویژه برای تخفیف‌های بالای 30 درصد
            ).distinct()
        return queryset

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(brand__name__icontains=value) |
            Q(categories__name__icontains=value) |
            Q(tags__name__icontains=value)
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

    def filter_is_new(self, queryset, name, value):
        if value is None:
            return queryset
        from django.utils import timezone
        import datetime
        seven_days_ago = timezone.now() - datetime.timedelta(days=7)  # تغییر از 30 روز به 7 روز
        if value:
            return queryset.filter(created_at__gte=seven_days_ago)
        return queryset.filter(created_at__lt=seven_days_ago)

    def filter_min_rating(self, queryset, name, value):
        if value is not None:
            return queryset.filter(rating__gte=value)
        return queryset

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
    
    # فیلترهای اصلی
    parent = ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        label='دسته‌بندی والد',
        help_text='فیلتر بر اساس دسته‌بندی والد'
    )
    
    is_root = BooleanFilter(method='filter_is_root', label='دسته‌بندی‌های اصلی')
    has_children = BooleanFilter(method='filter_has_children', label='دارای زیر دسته')
    
    # فیلترهای مرتب‌سازی
    sort_by_products = BooleanFilter(method='filter_sort_by_products', label='مرتب‌سازی بر اساس تعداد محصولات')
    sort_by_subcategories = BooleanFilter(method='filter_sort_by_subcategories', label='مرتب‌سازی بر اساس تعداد زیردسته‌ها')
    
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
            Q(description__icontains=value) |
            Q(brand__name__icontains=value)
        ).distinct()
    
    def filter_has_products(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(products__isnull=False).distinct()
        return queryset.filter(products__isnull=True).distinct()

    def filter_is_root(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(parent__isnull=True)
        return queryset.filter(parent__isnull=False)

    def filter_has_children(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(children__isnull=False).distinct()
        return queryset.filter(children__isnull=True).distinct()

    def filter_sort_by_products(self, queryset, name, value):
        if value:
            from django.db.models import Count
            return queryset.annotate(product_count=Count('products')).order_by('-product_count')
        return queryset

    def filter_sort_by_subcategories(self, queryset, name, value):
        if value:
            from django.db.models import Count
            return queryset.annotate(children_count=Count('children')).order_by('-children_count')
        return queryset

    class Meta:
        model = Category
        fields = {
            'brand': ['exact'],
            'spec_definitions': ['exact', 'in'],
        }


