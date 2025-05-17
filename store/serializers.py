from rest_framework import serializers
from .models import Product, Category, ProductFeature, ProductOption, Discount, Brand
from loan_calculator.models import LoanCondition, PrePaymentInstallment
from django.utils import timezone


class PrePaymentInstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrePaymentInstallment
        fields = ["id", "percent_of_initial_increased_price", "days_offset_for_payment", "order", "due_date_from_today"]

class LoanConditionSerializer(serializers.ModelSerializer):
    prepayment_installments = PrePaymentInstallmentSerializer(many=True, read_only=True)
    class Meta:
        model = LoanCondition
        fields = ["id", "title", "condition_type","product",
                  "guarantee_type", "has_guarantor", 
                  "condition_months", "annual_interest_rate_percent", 
                  "initial_increase_percent", "single_prepayment_percent",
                    "secondary_increase_percent", "delivery_days", "prepayment_installments"]
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

class ProductFeatureValueSerializer(serializers.ModelSerializer):
    feature_name = serializers.CharField(source='feature.name', read_only=True)
    
    class Meta:
        model = ProductFeature
        fields = ['id', 'feature', 'feature_name', 'value']

class ProductOptionSerializer(serializers.ModelSerializer):
    feature_name = serializers.CharField(source='feature.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True)
    
    class Meta:
        model = ProductOption
        fields = ['id', 'feature', 'feature_name', 'value', 'color', 'color_name', 'option_price']

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'name', 'percentage', 'start_date', 'end_date']

class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    feature_values = ProductFeatureValueSerializer(many=True, read_only=True)
    options = ProductOptionSerializer(many=True, read_only=True)
    discounts = DiscountSerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    active_discounts = serializers.SerializerMethodField()
    loan_conditions = LoanConditionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'categories', 'base_price_cash', 'description',
            'image', 'brand', 'feature_values', 'options',
            'discounts', 'active_discounts', 'loan_conditions'
        ]
    
    def get_active_discounts(self, obj):
        now = timezone.now()
        active_discounts = obj.discounts.filter(
            start_date__lte=now,
            end_date__gte=now
        )
        return DiscountSerializer(active_discounts, many=True).data 
