from rest_framework import serializers
from .models import Product, Category, ProductOption, Brand, Gallery, Feature, Color
from loan_calculator.serializers import LoanConditionSerializer
from django.utils import timezone
from django.db.models import Q


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

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'name', 'value', 'is_main_feature', 'category']

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'children', 'brand', 'features', 'slug', 'image']
    
    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data

class ProductOptionSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    final_price = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    gallery = GallerySerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductOption
        fields = ['id', 'color', 'option_price', 'quantity', 'is_active', 
                 'is_active_discount', 'discount', 'features', 'final_price', 'gallery']

    def get_final_price(self, obj):
        return obj.get_final_price()
        
    def get_features(self, obj):
        return FeatureSerializer(obj.product.feature.all(), many=True).data

class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    options = ProductOptionSerializer(many=True, read_only=True)
    loan_conditions = LoanConditionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'categories', 'description',
            'image', 'brand', 'features', 'options', 'loan_conditions', 
            'is_active'
        ]
