from rest_framework import serializers
from .models import (
    Product, Category, ProductOption, Brand, Gallery, 
    Specification, ProductSpecification , Color , Tag , Warranty, ArticleCategory, Article
)

from django.utils import timezone
from django.db.models import Q, Avg



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
    
    class Meta:
        model = Specification
        fields = ['id', 'category', 'name', 'slug', 'data_type', 'data_type_display', 'unit']

class ProductSpecificationSerializer(serializers.ModelSerializer):
    specification = SpecificationSerializer(read_only=True)
    value = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductSpecification
        fields = ['id', 'product', 'specification', 'value']
    
    def get_value(self, obj):
        return obj.value()

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True)
    spec_definitions = SpecificationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'children', 'brand', 
                 'spec_definitions', 'slug', 'image']
    
    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data

class ProductOptionSerializer(serializers.ModelSerializer):
    color = serializers.StringRelatedField()
    final_price = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()
    class Meta:
        model = ProductOption
        fields = ['id', 'color', 'option_price', 'quantity', 'is_active',
                'is_active_discount', 'discount', 'final_price', 'gallery']

    def get_final_price(self, obj):
        return obj.get_final_price()

    def get_gallery(self, obj):
        return [{'id': img.id, 'image': img.image.url if img.image else None, 'alt_text': img.alt_text} 
                for img in obj.gallery.all()]

    def get_tags(self, obj):
        return TagSerializer(obj.tags.all(), many=True).data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']




class WarrantySerializer(serializers.ModelSerializer):
    product_options = ProductOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Warranty
        fields = ['id', 'name',  'is_active', 'product_options']



class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    brand = serializers.StringRelatedField()
    options = ProductOptionSerializer(many=True, read_only=True)
    spec_values = ProductSpecificationSerializer(many=True, read_only=True)
    # loan_conditions = LoanConditionSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True , read_only=True)
    
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'categories', 'description',
            'image', 'brand', 'options', 'spec_values', 'loan_conditions',
            'is_active', 'tags'
        ] 
        
class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    category = ArticleCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ArticleCategory.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'content', 'image', 'category', 'category_id', 'created_at', 'updated_at', 'is_published']