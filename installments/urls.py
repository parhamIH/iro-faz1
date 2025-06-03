from django.urls import path
from .views import InstallmentCalculationAPIView

urlpatterns = [
    path('calculate/', InstallmentCalculationAPIView.as_view(), name='installment-calculate'),
]
