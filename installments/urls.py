from django.urls import path
from .views import InstallmentCalculationAPIView
from .views import CompanyInstallmentCalculationAPIView

urlpatterns = [

    path('calculate/', InstallmentCalculationAPIView.as_view(), name='installment-calculate'),
    path('company-calculate/', CompanyInstallmentCalculationAPIView.as_view(), name='company-installment-calculate'),
]
