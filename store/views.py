from django.shortcuts import render

# Create your from rest_framework import viewsets
from rest_framework import viewsets, permissions, status # Import status
from rest_framework.views import APIView # Import APIView
from rest_framework.response import Response # Import Response
from django.http import Http404 # Import Http404

from .models import Product, Category, InstallmentPlan, Discount
from .serializers import ProductSerializer, CategorySerializer, InstallmentPlanSerializer, DiscountSerializer
from .permissions import IsAdminOrReadOnly


# --- Product Views using APIView ---

class ProductListView(APIView):
    """List all products, or create a new product."""
    permission_classes = [IsAdminOrReadOnly]
    http_method_names= ["get","post"]
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
    """Retrieve, update or delete a product instance."""
    permission_classes = [IsAdminOrReadOnly]
    http_method_names= ["get","put","patch"]
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class categoriesView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ["get","post"]
    
    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True, context={'request': request}) 
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data, context={'request': request}) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CategoryView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    http_method_names= ["get","put","patch","delete"]
    
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)
        
    def put(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InstallmentPlanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = InstallmentPlan.objects.all()
    serializer_class = InstallmentPlanSerializer

class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminOrReadOnly]
