from rest_framework import serializers
from .models import Product, Category, ProductOption, Brand, Gallery
from loan_calculator.serializers import LoanConditionSerializer, PrePaymentInstallmentSerializer
from django.utils import timezone
from django.db.models import Q


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id', 'product', 'image', 'alt_text']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'logo']

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'children', 'brand']
    
    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data

class ProductOptionSerializer(serializers.ModelSerializer):
    feature_name = serializers.CharField(source='feature.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True)
    final_price = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductOption
        fields = ['id', 'feature', 'feature_name', 'feature_value', 'color', 'color_name', 'option_price', 'is_active_discount', 'discount', 'final_price']

    def get_final_price(self, obj):
        return obj.get_final_price()

class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    options = ProductOptionSerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    loan_conditions = LoanConditionSerializer(many=True, read_only=True)
    gallery = GallerySerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'categories', 'description',
            'image', 'brand', 'options', 'loan_conditions', 'gallery'
        ]
