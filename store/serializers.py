from rest_framework import serializers
from .models import Product, Category, ProductFeatureValue, ProductOption, InstallmentPlan, Discount, Brand
from django.utils import timezone

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'logo']

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'children', 'brand']
    
    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data

class ProductFeatureValueSerializer(serializers.ModelSerializer):
    feature_name = serializers.CharField(source='feature.name', read_only=True)
    
    class Meta:
        model = ProductFeatureValue
        fields = ['id', 'feature', 'feature_name', 'value']

class ProductOptionSerializer(serializers.ModelSerializer):
    feature_name = serializers.CharField(source='feature.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True)
    
    class Meta:
        model = ProductOption
        fields = ['id', 'feature', 'feature_name', 'value', 'color', 'color_name', 'price_change']

class InstallmentPlanSerializer(serializers.ModelSerializer):
    monthly_installment = serializers.DecimalField(
        read_only=True,
        max_digits=12,
        decimal_places=2
    )
    total_payment = serializers.DecimalField(
        read_only=True,
        max_digits=12,
        decimal_places=2
    )
    
    class Meta:
        model = InstallmentPlan
        fields = ['id', 'title', 'months', 'prepayment', 'monthly_installment', 'total_payment', 'discounts']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['monthly_installment'] = instance.calculate_monthly_installment()
        data['total_payment'] = instance.total_payment()
        return data

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'name', 'percentage', 'start_date', 'end_date']

class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    feature_values = ProductFeatureValueSerializer(many=True, read_only=True)
    options = ProductOptionSerializer(many=True, read_only=True)
    installment_plans = InstallmentPlanSerializer(many=True, read_only=True)
    discounts = DiscountSerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    active_discounts = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'categories', 'base_price_cash', 'description',
            'image', 'brand', 'feature_values', 'options', 'installment_plans',
            'discounts', 'active_discounts'
        ]
    
    def get_active_discounts(self, obj):
        now = timezone.now()
        active_discounts = obj.discounts.filter(
            start_date__lte=now,
            end_date__gte=now
        )
        return DiscountSerializer(active_discounts, many=True).data 
