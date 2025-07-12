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
    OrderSerializer,
    OrderCreateSerializer,
)
from rest_framework.permissions import IsAuthenticated


class CartDetailAPIView(APIView):
    authentication_classes = []  # اجازه دسترسی بدون احراز هویت

    def get(self, request):
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        user = request.user if request.user.is_authenticated else None

        if user:
            cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)
        else:
            cart, _ = Cart.objects.get_or_create(session_key=session_key, is_paid=False)

        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemAddAPIView(APIView):
    authentication_classes = []

    def post(self, request):
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        user = request.user if request.user.is_authenticated else None

        if user:
            cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)
        else:
            cart, _ = Cart.objects.get_or_create(session_key=session_key, is_paid=False)

        serializer = CartItemCreateSerializer(data=request.data)
        if serializer.is_valid():
            package = serializer.validated_data['package']
            count = serializer.validated_data.get('count', 1)

            if count < 1:
                return Response({"detail": "تعداد باید حداقل 1 باشد."}, status=status.HTTP_400_BAD_REQUEST)

            cart_item, created = CartItem.objects.get_or_create(cart=cart, package=package)
            if not created:
                cart_item.count += count
            else:
                cart_item.count = count
            cart_item.save()

            return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemUpdateAPIView(APIView):
    def patch(self, request, item_id):
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key

        if user:
            cart = get_object_or_404(Cart, user=user, is_paid=False)
        else:
            if not session_key:
                return Response({"detail": "بدون سشن کی امکان‌پذیر نیست."}, status=status.HTTP_400_BAD_REQUEST)
            cart = get_object_or_404(Cart, session_key=session_key, is_paid=False)

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
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key

        if user:
            cart = get_object_or_404(Cart, user=user, is_paid=False)
        else:
            if not session_key:
                return Response({"detail": "بدون سشن کی امکان‌پذیر نیست."}, status=status.HTTP_400_BAD_REQUEST)
            cart = get_object_or_404(Cart, session_key=session_key, is_paid=False)

        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        return Response({"detail": "آیتم حذف شد."}, status=status.HTTP_204_NO_CONTENT)


class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # فقط کاربر وارد شده اجازه ساخت سفارش دارد

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
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        user = request.user
        order = get_object_or_404(Order, id=order_id, user=user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
