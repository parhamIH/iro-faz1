from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import InstallmentParameter
from .serializers import InstallmentCalculationInputSerializer
# installments/views.py

from .utils import calculate_loan_payments

# ... بقیه کد API که قبلا نوشتی


class InstallmentCalculationAPIView(APIView):
    def post(self, request):
        serializer = InstallmentCalculationInputSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            product_price = data['product_price']
            down_payment = data['down_payment']
            param = get_object_or_404(InstallmentParameter, pk=data['installment_param_id'])

            # 1- قیمت افزایش‌یافته اولیه
            increased_price = product_price + (product_price * param.initial_increase_percent / 100)

            # 2- قیمت پس از پیش‌پرداخت
            remaining_price = increased_price - down_payment

            # 3- افزایش قیمت پس از پیش‌پرداخت
            post_increased_price = remaining_price * (1 + param.post_down_payment_increase_percent / 100)

            # نرخ بهره ماهیانه از درصد سالیانه بانک (تقسیم بر 12)
            monthly_interest_rate = (param.bank_tax_interest_percent / 100) / 12

            # مبلغ وام نهایی (می‌تونی اینجا تصمیم بگیری اگر باید دوباره ضریب بازپرداخت بزنی)
            final_loan_amount = post_increased_price  # بدون اضافه کردن مجدد دوره چون تو فرمول اقساط حساب میشه

            # محاسبه اقساط ماهیانه، کل بازپرداخت و سود کل وام
            loan_results = calculate_loan_payments(final_loan_amount, monthly_interest_rate, param.repayment_period)

            return Response({
                "increased_price": round(increased_price, 2),
                "remaining_price": round(remaining_price, 2),
                "post_increased_price": round(post_increased_price, 2),
                "final_loan_amount": round(final_loan_amount, 2),
                "monthly_payment": loan_results["monthly_payment"],
                "total_payment": loan_results["total_payment"],
                "total_interest": loan_results["total_interest"],
                "repayment_period_months": param.repayment_period,
                "guarantee_method": param.get_method_display(),
                "check_guarantee_period_months": param.check_guarantee_period,
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
