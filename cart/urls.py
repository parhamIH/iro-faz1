from django.urls import path
from .views import (
    CartDetailAPIView,
    CartItemAddAPIView,
    CartItemUpdateAPIView,
    CartItemDeleteAPIView,
    OrderCreateAPIView,
    OrderDetailAPIView,
)

app_name = 'cart'  # برای namespace کردن مسیرها

urlpatterns = [
    path('', CartDetailAPIView.as_view(), name='cart-detail'),
    path('items/add/', CartItemAddAPIView.as_view(), name='cartitem-add'),
    path('items/<int:item_id>/update/', CartItemUpdateAPIView.as_view(), name='cartitem-update'),
    path('items/<int:item_id>/delete/', CartItemDeleteAPIView.as_view(), name='cartitem-delete'),
    path('order/create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('order/<int:order_id>/', OrderDetailAPIView.as_view(), name='order-detail'),
]