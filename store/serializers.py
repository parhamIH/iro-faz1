from rest_framework import serializers
from .models import (
    Product, Category, ProductOption, Brand, Gallery, 
    Specification, ProductSpecification, Color, Tag, Warranty, SpecificationGroup
)

from django.utils import timezone
from django.db.models import Q, Avg


class GallerySerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.product.title', read_only=True)
    color_name = serializers.CharField(source='product.color.name', read_only=True)
    option_id = serializers.IntegerField(source='product.id', read_only=True)

    class Meta:
        model = Gallery
        fields = ['id', 'product', 'option_id', 'product_title', 'color_name', 'image', 'alt_text']


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

    class Meta:
        model = Specification
        fields = ['id', 'name', 'slug', 'data_type', 'data_type_display', 'unit']


class ProductSpecificationSerializer(serializers.ModelSerializer):
    specification = SpecificationSerializer(read_only=True)
    value = serializers.SerializerMethodField()

    class Meta:
        model = ProductSpecification
        fields = ['id', 'product', 'specification', 'value', "is_main"]

    def get_value(self, obj):
        return obj.value()


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


class ParentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True)
    spec_definitions = SpecificationSerializer(many=True, read_only=True)
    parent = ParentCategorySerializer(read_only=True)  # نمایش نام و slug والد

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'children', 'brand',
                 'spec_definitions', 'slug', 'image']

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data


class ProductOptionSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)  # اصلاح به جای StringRelatedField
    final_price = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()

    class Meta:
        model = ProductOption
        fields = ['id', 'color', 'option_price', 'quantity', 'is_active',
                  'is_active_discount', 'discount', 'final_price', 'gallery']

    def get_final_price(self, obj):
        return obj.get_final_price()

    def get_gallery(self, obj):
        return [
            {
                'id': img.id,
                'option_id': obj.id,
                'image': img.image.url if img.image else None,
                'alt_text': img.alt_text
            }
            for img in obj.gallery.all()
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class WarrantySerializer(serializers.ModelSerializer):
    product_options = ProductOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Warranty
        fields = ['id', 'name', 'is_active', 'product_options']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)  # تغییر داده شده به BrandSerializer
    options = ProductOptionSerializer(many=True, read_only=True)
    spec_groups = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'category', 'description',
            'image', 'brand', 'options', 'spec_groups', 'is_active', 'tags'
        ]

    def get_spec_groups(self, obj):
        groups = SpecificationGroup.objects.filter(
            specifications__values__product=obj
        ).distinct()

        serializer = SpecificationGroupSerializer(groups, many=True, context={'product': obj})
        return serializer.data
