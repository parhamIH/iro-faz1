from django.shortcuts import render

# Create your from rest_framework import viewsets
from rest_framework import viewsets
from .models import Product, Category, InstallmentPlan, Discount
from .serializers import ProductSerializer, CategorySerializer, InstallmentPlanSerializer, DiscountSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class InstallmentPlanViewSet(viewsets.ModelViewSet):
    queryset = InstallmentPlan.objects.all()
    serializer_class = InstallmentPlanSerializer

class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
