from rest_framework import serializers
from .models import Product, Category, Feature, ProductFeatureValue, ProductOption, InstallmentPlan, Discount

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductFeatureValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeatureValue
        fields = '__all__'

class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = '__all__'

class InstallmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPlan
        fields = '__all__'

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    feature_values = ProductFeatureValueSerializer(many=True, read_only=True)
    options = ProductOptionSerializer(many=True, read_only=True)
    installment_plans = InstallmentPlanSerializer(many=True, read_only=True)
    discounts = DiscountSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
