from rest_framework import serializers
from .models import Cart, CartItem, Order
from store.models import ProductOption


class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = ['id', 'option_price', 'quantity', 'color', 'product']


class CartItemSerializer(serializers.ModelSerializer):
    package = ProductOptionSerializer(read_only=True)
    package_id = serializers.PrimaryKeyRelatedField(queryset=ProductOption.objects.all(), source='package', write_only=True)
    total_final_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'package', 'package_id', 'count', 'total_final_price']

    def get_total_final_price(self, obj):
        return float(obj.total_final_price)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    item_count = serializers.IntegerField(source='item_count', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_key', 'is_paid', 'created_date', 'updated_date', 'item_count', 'total_price', 'items']
        read_only_fields = ['user', 'is_paid', 'created_date', 'updated_date', 'session_key']

    def get_total_price(self, obj):
        return float(obj.total_price())


class CartItemCreateSerializer(serializers.ModelSerializer):
    package_id = serializers.PrimaryKeyRelatedField(queryset=ProductOption.objects.all(), source='package')

    class Meta:
        model = CartItem
        fields = ['id', 'package_id', 'count']


class OrderSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'cart', 'order_number', 'order_date', 'payment_method', 'payment_status',
            'shipping_method', 'shipping_cost', 'total_price', 'discount_code', 'discount_amount',
            'shipping_date', 'delivery_date', 'jalali_delivery_date', 'notes', 'status'
        ]
        read_only_fields = ['user', 'order_number', 'order_date', 'total_price']


class OrderCreateSerializer(serializers.ModelSerializer):
    cart_id = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all(), source='cart')

    class Meta:
        model = Order
        fields = [
            'cart_id', 'payment_method', 'shipping_method', 'shipping_cost',
            'discount_code', 'discount_amount', 'shipping_date', 'delivery_date', 'jalali_delivery_date', 'notes'
        ]
