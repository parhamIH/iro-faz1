from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import InstallmentParameter, CompanyInstallmentParameter
from store.models import Product
from .serializers import InstallmentCalculationInputSerializer, CompanyInstallmentCalculationInputSerializer
from .utils import calculate_loan_payments, calculate_company_installment, generate_company_checks
from datetime import timedelta, date
from decimal import Decimal, ROUND_HALF_UP
import jdatetime


def convert_to_persian_digits(text):
    en_to_fa_digits = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return text.translate(en_to_fa_digits)

def format_amount(amount):
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    formatted = f"{amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,}"
    return convert_to_persian_digits(formatted)


class InstallmentCalculationAPIView(APIView):
    def post(self, request):
        serializer = InstallmentCalculationInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_price = Decimal(str(data['product_price']))
        down_payment = Decimal(str(data['down_payment']))
        product_id = data.get('product_id')

        # یافتن پارامتر قسط مرتبط با محصول، یا پیش‌فرض
        param = None
        if product_id:
            param = InstallmentParameter.objects.filter(products__id=product_id).first()
        if not param:
            param = InstallmentParameter.objects.filter(products=None).first()
        if not param:
            return Response({'error': 'هیچ پارامتر قسطی یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        # ادامه محاسبه اقساط
        initial_increase_percent = Decimal(str(param.initial_increase_percent))
        post_down_payment_increase_percent = Decimal(str(param.post_down_payment_increase_percent))
        bank_tax_interest_percent = Decimal(str(param.bank_tax_interest_percent))

        increased_price = product_price + (product_price * initial_increase_percent / Decimal("100"))
        remaining_price = increased_price - down_payment
        post_increased_price = remaining_price * (Decimal("1") + post_down_payment_increase_percent / Decimal("100"))

        monthly_interest_rate = (bank_tax_interest_percent / Decimal("100")) / Decimal("12")
        final_loan_amount = post_increased_price

        loan_results = calculate_loan_payments(final_loan_amount, monthly_interest_rate, param.repayment_period)

        check_due_date = date.today() + timedelta(days=param.check_guarantee_period * 30)
        jdate = jdatetime.date.fromgregorian(date=check_due_date)
        jdate_str_fa = convert_to_persian_digits(jdate.strftime("%Y/%m/%d"))

        total_with_interest = final_loan_amount + Decimal(str(loan_results["total_interest"]))
        if param.method == InstallmentParameter.METHOD_CHECK:
            guarantee_amount = total_with_interest * Decimal("1.25")
            guarantee_type_display = "چک"
        elif param.method == InstallmentParameter.METHOD_PROMISSORY:
            guarantee_amount = total_with_interest * Decimal("1.5")
            guarantee_type_display = "سفته"
        else:
            guarantee_amount = Decimal("0")
            guarantee_type_display = "نامشخص"

        check_message = f"لطفاً چک را در تاریخ {jdate_str_fa} به شرکت تحویل دهید."

        return Response({
            "increased_price": format_amount(increased_price),
            "remaining_price": format_amount(remaining_price),
            "post_increased_price": format_amount(post_increased_price),
            "final_loan_amount": format_amount(final_loan_amount),
            "monthly_payment": format_amount(loan_results['monthly_payment']),
            "total_payment": format_amount(loan_results['total_payment']),
            "total_interest": format_amount(loan_results['total_interest']),
            "repayment_period_months": convert_to_persian_digits(str(param.repayment_period)),
            "guarantee_method": guarantee_type_display,
            "guarantee_amount": format_amount(guarantee_amount),
            "check_guarantee_period_months": convert_to_persian_digits(str(param.check_guarantee_period)),
            "check_due_date": jdate_str_fa,
            "check_due_message": check_message,
        })


class CompanyInstallmentCalculationAPIView(APIView):
    def post(self, request):
        serializer = CompanyInstallmentCalculationInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_price = data['product_price']
        down_payment = data['down_payment']
        product_id = data.get('product_id')

        # یافتن پارامتر قسط شرکتی بر اساس محصول
        param = None
        if product_id:
            param = CompanyInstallmentParameter.objects.filter(products__id=product_id).first()
        if not param:
            param = CompanyInstallmentParameter.objects.filter(products=None).first()
        if not param:
            return Response({'error': 'هیچ پارامتر اقساط شرکتی یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        result = calculate_company_installment(product_price, down_payment, param)
        checks = generate_company_checks(result['monthly_payment'], result['repayment_period'])

        return Response({
            "increased_price": result['increased_price'],
            "remaining_price": result['remaining_price'],
            "monthly_payment": result['monthly_payment'],
            "total_interest": result['total_interest'],
            "repayment_period": result['repayment_period'],
            "checks": checks,
            "parameter_id_used": result.get('parameter_id_used', None),
        })
