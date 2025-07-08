from django.urls import path
from .views import CategoryInstallmentOptionsAPIView
from .views import (
    InstallmentCalculationAPIView,
    CompanyInstallmentCalculationAPIView,
    CategoryInstallmentOptionsAPIView,
)

urlpatterns = [
    path('calculate/', InstallmentCalculationAPIView.as_view(), name='installment-calculate'),
    path('company-calculate/', CompanyInstallmentCalculationAPIView.as_view(), name='company-installment-calculate'),
    path('category-installments/<int:category_id>/', CategoryInstallmentOptionsAPIView.as_view(), name='category-installments'),
    
]
