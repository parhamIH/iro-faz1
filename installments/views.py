from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import timedelta, date
from decimal import Decimal, ROUND_HALF_UP
import jdatetime

from .models import InstallmentParameter, CompanyInstallmentParameter
from store.models import Category
from .serializers import (
    InstallmentCalculationInputSerializer,
    CompanyInstallmentCalculationInputSerializer,
)
from .utils import (
    calculate_loan_payments,
    calculate_company_installment,
    generate_company_checks,
)

from drf_yasg.utils import swagger_auto_schema


def convert_to_persian_digits(text):
    en_to_fa_digits = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return str(text).translate(en_to_fa_digits)


def format_amount(amount):
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    formatted = f"{amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,}"
    return convert_to_persian_digits(formatted)


class InstallmentCalculationAPIView(APIView):
    @swagger_auto_schema(request_body=InstallmentCalculationInputSerializer)
    def post(self, request):
        serializer = InstallmentCalculationInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_price = Decimal(str(data['product_price']))
        down_payment = Decimal(str(data['down_payment']))
        installment_param_id = data['installment_param_id']
        category_id = data.get("category_id")

        param = get_object_or_404(InstallmentParameter, pk=installment_param_id)

        # اصلاح شده به applicable_categories
        if param.applicable_categories.exists():
            if not category_id:
                return Response({
                    "error": "دسته‌بندی محصول مشخص نشده است."
                }, status=status.HTTP_400_BAD_REQUEST)

            category = get_object_or_404(Category, pk=category_id)
            if not param.applicable_categories.filter(pk=category.pk).exists():
                return Response({
                    "error": "این روش اقساط برای این دسته‌بندی مجاز نیست.",
                    "category_id": category.id,
                    "category_name": category.name,
                    "allowed_categories": list(param.applicable_categories.values('id', 'name')),
                }, status=status.HTTP_400_BAD_REQUEST)

        # محاسبات افزایش قیمت
        increased_price = product_price + (product_price * param.initial_increase_percent / Decimal("100"))
        remaining_price = increased_price - down_payment
        post_increased_price = remaining_price * (Decimal("1") + param.post_down_payment_increase_percent / Decimal("100"))
        monthly_interest_rate = (param.bank_tax_interest_percent / Decimal("100")) / Decimal("12")
        final_loan_amount = post_increased_price

        loan_results = calculate_loan_payments(final_loan_amount, monthly_interest_rate, param.repayment_period)

        check_due_date = date.today() + timedelta(days=param.check_guarantee_period * 30)
        jdate_str_fa = convert_to_persian_digits(jdatetime.date.fromgregorian(date=check_due_date).strftime("%Y/%m/%d"))

        total_with_interest = final_loan_amount + loan_results["total_interest"]

        if param.method == InstallmentParameter.METHOD_CHECK:
            guarantee_amount = total_with_interest * Decimal("1.25")
            guarantee_type = "چک"
        elif param.method == InstallmentParameter.METHOD_PROMISSORY:
            guarantee_amount = total_with_interest * Decimal("1.5")
            guarantee_type = "سفته"
        else:
            guarantee_amount = Decimal("0")
            guarantee_type = "نامشخص"

        return Response({
            "increased_price": format_amount(increased_price),
            "remaining_price": format_amount(remaining_price),
            "post_increased_price": format_amount(post_increased_price),
            "final_loan_amount": format_amount(final_loan_amount),
            "monthly_payment": format_amount(loan_results['monthly_payment']),
            "total_payment": format_amount(loan_results['total_payment']),
            "total_interest": format_amount(loan_results['total_interest']),
            "repayment_period_months": convert_to_persian_digits(param.repayment_period),
            "guarantee_method": guarantee_type,
            "guarantee_amount": format_amount(guarantee_amount),
            "check_due_date": jdate_str_fa,
            "check_due_message": f"لطفاً چک را در تاریخ {jdate_str_fa} به شرکت تحویل دهید.",
        })

    def get(self, request):
        params = InstallmentParameter.objects.all()
        result = []
        for param in params:
            categories = param.applicable_categories.values('id', 'name') if hasattr(param, 'applicable_categories') else []
            result.append({
                'id': param.id,
                'name': getattr(param, 'name', ''),
                'categories': list(categories),
            })
        return Response(result)


class CompanyInstallmentCalculationAPIView(APIView):
    @swagger_auto_schema(request_body=CompanyInstallmentCalculationInputSerializer)
    def post(self, request):
        serializer = CompanyInstallmentCalculationInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_price = data['product_price']
        down_payment = data['down_payment']
        installment_param_id = data['installment_param_id']
        category_id = data.get('category_id')

        param = get_object_or_404(CompanyInstallmentParameter, pk=installment_param_id)

        # اصلاح شده به applicable_categories
        if param.applicable_categories.exists():
            if not category_id:
                return Response({'error': 'دسته‌بندی محصول مشخص نشده است.'}, status=status.HTTP_400_BAD_REQUEST)
            if not param.applicable_categories.filter(pk=category_id).exists():
                return Response({'error': 'این روش اقساطی برای این دسته‌بندی قابل استفاده نیست.'}, status=status.HTTP_400_BAD_REQUEST)

        result = calculate_company_installment(product_price, down_payment, param)
        checks = generate_company_checks(result['monthly_payment'], result['repayment_period'])

        return Response({
            "increased_price": format_amount(result['increased_price']),
            "remaining_price": format_amount(result['remaining_price']),
            "monthly_payment": format_amount(result['monthly_payment']),
            "total_interest": format_amount(result['total_interest']),
            "repayment_period": convert_to_persian_digits(result['repayment_period']),
            "checks": checks,
        })


class CategoryInstallmentOptionsAPIView(APIView):
    """
    نمایش روش‌های اقساطی مرتبط با یک دسته‌بندی خاص
    """

    def get(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "دسته‌بندی یافت نشد."}, status=404)

        applicable_params = InstallmentParameter.objects.filter(applicable_categories=category)
        data = [
            {
                "id": param.id,
                "name": getattr(param, "name", ""),
            }
            for param in applicable_params
        ]
        return Response(data)
