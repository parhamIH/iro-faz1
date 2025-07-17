from rest_framework import serializers
from .models import (
    Product, Category, ProductOption, Brand, Gallery,
    Specification, ProductSpecification , Color , Tag , Warranty,SpecificationGroup
)
from .filters import ProductFilter
from .models import Product
from django.utils import timezone
from django.db.models import Q, Avg,Min



class GallerySerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.product.title', read_only=True)
    color_name = serializers.CharField(source='product.color.name', read_only=True)

    class Meta:
        model = Gallery
        fields = ['id', 'product', 'product_title', 'color_name', 'image', 'alt_text']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'logo', 'slug']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_code']

class SpecificationSerializer(serializers.ModelSerializer):
    data_type_display = serializers.CharField(source='get_data_type_display', read_only=True)
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Specification
        fields = ['id', 'categories', 'name', 'data_type', 'data_type_display', 'unit']

    def get_categories(self, obj):
        return [{'id': cat.id, 'name': cat.name,} for cat in obj.categories.all()]

class ProductSpecificationSerializer(serializers.ModelSerializer):
    specification = SpecificationSerializer(read_only=True)
    value = serializers.SerializerMethodField()

    class Meta:
        model = ProductSpecification
        fields = ['id', 'product', 'specification', 'value' , "is_main"]

    def get_value(self, obj):
        return obj.value()

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True,many=True)
    spec_definitions = SpecificationSerializer(many=True, read_only=True)
    products = serializers.SerializerMethodField()
    spec_value_choices = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'parent', 'children', 'brand',
            'spec_definitions', 'slug', 'image','icon', 'products', 'spec_value_choices'
        ]

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data

    def get_products(self, obj):
        from .models import Product
        qs = Product.objects.filter(categories=obj)
        return ProductSerializer(qs, many=True, context=self.context).data

    def get_spec_value_choices(self, obj):
        from .serializers import SpecificationWithValuesSerializer
        specs = obj.spec_definitions.all()
        serializer = SpecificationWithValuesSerializer(specs, many=True, context={'category': obj})
        return serializer.data

class ProductOptionSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    final_price = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()
    discount_time = serializers.SerializerMethodField()  # تغییر نام فیلد

    class Meta:
        model = ProductOption
        fields = [
            'id', 'color', 'option_price', 'quantity', 'is_active',
            'is_active_discount', 'discount', 'final_price', 'gallery', 'discount_time'
        ]

    def get_final_price(self, obj):
        return obj.get_final_price()

    def get_gallery(self, obj):
        return [{'id': img.id, 'image': img.image.url if img.image else None, 'alt_text': img.alt_text}
                for img in obj.gallery.all()]

    def get_tags(self, obj):
        return TagSerializer(obj.tags.all(), many=True).data

    def get_discount_time(self, obj):
        if obj.discount_start_date and obj.discount_end_date:
            duration = obj.discount_end_date - obj.discount_start_date
            return duration.total_seconds()
        return None

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']



class WarrantySerializer(serializers.ModelSerializer):
    product_options = ProductOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Warranty
        fields = ['id', 'name',  'is_active', 'product_options']

class SpecificationGroupSerializer(serializers.ModelSerializer):
    specifications = serializers.SerializerMethodField()
    
    class Meta:
        model = SpecificationGroup
        fields = ['id', 'name', 'specifications']
    
    def get_specifications(self, obj):
        product = self.context.get('product')
        spec_values = ProductSpecification.objects.filter(
            product=product,
            specification__group=obj
        ).select_related('specification')
        return ProductSpecificationSerializer(spec_values, many=True).data

class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    brand = serializers.StringRelatedField()
    options = ProductOptionSerializer(many=True, read_only=True)
    spec_values = ProductSpecificationSerializer(many=True, read_only=True)
    spec_groups = serializers.SerializerMethodField()
    similar_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'categories', 'description',
            'image', 'brand', 'options', 'spec_values',
            'is_active', 'tags', 'spec_groups', 'similar_products',
        ]

    def get_spec_groups(self, obj):
        serializer = SpecificationGroupSerializer( many=True, context={'product': obj})
        return serializer.data

    def get_similar_products(self, obj):
        # پیدا کردن دسته‌بندی‌های برگ
        leaf_categories = [cat for cat in obj.categories.all() if hasattr(cat, 'is_leaf_node') and cat.is_leaf_node()]
        if not leaf_categories:
            return []
        # ویژگی‌های اصلی محصول فعلی
        from store.models import ProductSpecification, Product
        main_specs = ProductSpecification.objects.filter(product=obj, is_main=True)
        main_spec_dict = {ps.specification_id: ps.specification_value for ps in main_specs}
        # رنج قیمت
        base_price = obj.options.aggregate(min_price=Min('option_price'))['min_price'] or 0
        price_lower = base_price * 0.8
        price_upper = base_price * 1.2
        # محصولات مشابه
        similar_products = Product.objects.filter(
            categories__in=leaf_categories,
            is_active=True,
            options__option_price__gte=price_lower,
            options__option_price__lte=price_upper,
        ).exclude(id=obj.id)
        # فیلتر بر اساس ویژگی‌های اصلی
        for spec_id, value in main_spec_dict.items():
            similar_products = similar_products.filter(
                spec_values__specification_id=spec_id,
                spec_values__specification_value=value,
                spec_values__is_main=True
            )
        similar_products = similar_products.distinct()[:10]
        return ProductCompactSerializer(similar_products, many=True).data

class ProductCompactSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField()
    min_price = serializers.SerializerMethodField()
    image = serializers.ImageField()
    options = ProductOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'brand', 'min_price', 'image', 'options']

    def get_min_price(self, obj):
        return obj.options.aggregate(min=Min('option_price'))['min']


    tags = TagSerializer(many=True , read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'categories', 'description',
            'image', 'brand', 'options', 'spec_values',
            'is_active', 'tags','spec_groups',
        ]

class SpecificationWithValuesSerializer(serializers.ModelSerializer):

    value = serializers.SerializerMethodField()

    class Meta:
        model = Specification
        fields = ['id', 'name', 'data_type', 'unit' , 'value']

    def get_value(self, obj):
        category = self.context.get('category')
        if not category:
            return []
        from .models import ProductSpecification
        qs = ProductSpecification.objects.filter(
            specification=obj,
            product__categories=category
        )
        # اگر می‌خواهید value لیست دیکشنری باشد:
        return [
            {"id": ps.id, "value": ps.specification_value}
            for ps in qs.distinct('specification_value')
        ]


class CategorySpecificationWithValuesSerializer(serializers.ModelSerializer):
    specifications = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'specifications']

    def get_specifications(self, obj):
        specs = obj.spec_definitions.all()
        return SpecificationWithValuesSerializer(specs, many=True, context={'category': obj}).data



