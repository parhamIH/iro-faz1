from django.urls import path
from .views import InstallmentCalculationAPIView, CompanyInstallmentCalculationAPIView

urlpatterns = [
    path('calculate/', InstallmentCalculationAPIView.as_view(), name='installment-calculate'),
    path('calculate/company/', CompanyInstallmentCalculationAPIView.as_view(), name='company-installment-calculate'),
]
