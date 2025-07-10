from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cart, CartItem, Order
from store.models import ProductOption
from .serializers import (
    CartSerializer,
    CartItemCreateSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderCreateSerializer,
)
from django.utils import timezone

class CartDetailAPIView(APIView):
    def get(self, request):
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user, is_paid=False)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemAddAPIView(APIView):
    def post(self, request):
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)

        serializer = CartItemCreateSerializer(data=request.data)
        if serializer.is_valid():
            package = serializer.validated_data['package']
            count = serializer.validated_data.get('count', 1)

            cart_item, created = CartItem.objects.get_or_create(cart=cart, package=package)
            if not created:
                cart_item.count += count
            else:
                cart_item.count = count
            cart_item.save()

            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemUpdateAPIView(APIView):
    def patch(self, request, item_id):
        user = request.user
        cart = get_object_or_404(Cart, user=user, is_paid=False)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        serializer = CartItemCreateSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            count = serializer.validated_data.get('count')
            if count is not None:
                if count <= 0:
                    cart_item.delete()
                    return Response({"detail": "آیتم حذف شد."}, status=status.HTTP_204_NO_CONTENT)
                else:
                    cart_item.count = count
                    cart_item.save()
                    return Response({"detail": "تعداد آیتم به‌روزرسانی شد."})
            return Response({"detail": "مقدار count معتبر نیست."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemDeleteAPIView(APIView):
    def delete(self, request, item_id):
        user = request.user
        cart = get_object_or_404(Cart, user=user, is_paid=False)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        return Response({"detail": "آیتم حذف شد."}, status=status.HTTP_204_NO_CONTENT)


class OrderCreateAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        user = request.user
        cart = get_object_or_404(Cart, user=user, is_paid=False)

        if cart.cartitem_set.count() == 0:
            return Response({"detail": "سبد خرید خالی است."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(user=user, cart=cart)
            cart.is_paid = True
            cart.save()

            order_serializer = OrderSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailAPIView(APIView):
    def get(self, request, order_id):
        user = request.user
        order = get_object_or_404(Order, id=order_id, user=user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
