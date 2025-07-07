from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import InstallmentParameter
from .serializers import InstallmentCalculationInputSerializer
from .utils import calculate_loan_payments
from datetime import timedelta, date
import jdatetime
from decimal import Decimal, ROUND_HALF_UP
from decimal import Decimal
from .models import CompanyInstallmentParameter
from .serializers import CompanyInstallmentCalculationInputSerializer
from .utils import calculate_company_installment, generate_company_checks


def convert_to_persian_digits(text):
    en_to_fa_digits = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return text.translate(en_to_fa_digits)

def format_amount(amount):
    # تبدیل هر عددی به Decimal
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))  # اطمینان از Decimal بودن
    formatted = f"{amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,}"
    return convert_to_persian_digits(formatted)


class InstallmentCalculationAPIView(APIView):
   from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import InstallmentParameter
from store.models import Category
from .serializers import InstallmentCalculationInputSerializer
from .utils import calculate_loan_payments
from datetime import timedelta, date
import jdatetime
from decimal import Decimal, ROUND_HALF_UP

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
        installment_param_id = data['installment_param_id']
        category_id = request.query_params.get("category_id")

        param = get_object_or_404(InstallmentParameter, pk=installment_param_id)

        # اگر کتگوری ارسال شده باشد، بررسی شود که این قسط در آن مجاز است
        # if category_id:
        #     category = get_object_or_404(Category, pk=category_id)
        #     if param.categories.exists() and not param.categories.filter(pk=category.pk).exists():
        #         return Response({
        #             "error": "این روش اقساط برای این دسته‌بندی مجاز نیست."
        #         }, status=status.HTTP_400_BAD_REQUEST)
        if category_id:
            category = get_object_or_404(Category, pk=category_id)
            if param.categories.exists():
                if not param.categories.filter(pk=category.pk).exists():
                    return Response({
                        "error": "این روش اقساط برای این دسته‌بندی مجاز نیست.",
                        "debug_category_id": category.id,
                        "debug_category_name": category.name,
                        "param_id": param.id,
                        "param_categories": list(param.categories.values('id', 'name')),
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # دسته‌بندی مجاز است
                    return Response({
                        "message": "این روش اقساط برای این دسته‌بندی مجاز است.",
                        "debug_category_id": category.id,
                        "debug_category_name": category.name,
                        "param_id": param.id,
                        "param_categories": list(param.categories.values('id', 'name')),
                    })
            else:
                # پارامتر اقساط به هیچ دسته‌ای اختصاص داده نشده، یعنی پیش‌فرض برای همه
                return Response({
                    "message": "این پارامتر اقساط به هیچ دسته‌ای اختصاص داده نشده، یعنی پیش‌فرض برای همه دسته‌هاست.",
                    "param_id": param.id,
                    "param_categories": [],
                })

        # افزایش اولیه
        increased_price = product_price + (product_price * param.initial_increase_percent / Decimal("100"))

        # بعد از پیش‌پرداخت
        remaining_price = increased_price - down_payment

        # افزایش نهایی
        post_increased_price = remaining_price * (Decimal("1") + param.post_down_payment_increase_percent / Decimal("100"))

        # نرخ بهره ماهانه
        monthly_interest_rate = (param.bank_tax_interest_percent / Decimal("100")) / Decimal("12")
        final_loan_amount = post_increased_price

        # محاسبه اقساط
        loan_results = calculate_loan_payments(final_loan_amount, monthly_interest_rate, param.repayment_period)

        # تاریخ سررسید چک
        check_due_date = date.today() + timedelta(days=param.check_guarantee_period * 30)
        jdate = jdatetime.date.fromgregorian(date=check_due_date)
        jdate_str_fa = convert_to_persian_digits(jdate.strftime("%Y/%m/%d"))

        # مبلغ ضمانت
        total_with_interest = final_loan_amount + loan_results["total_interest"]
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
    """
    API برای محاسبه اقساط براساس شرایط فروش شرکتی، با پشتیبانی از دسته‌بندی
    """

    def post(self, request):
        serializer = CompanyInstallmentCalculationInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_price = serializer.validated_data['product_price']
        down_payment = serializer.validated_data['down_payment']
        installment_param_id = serializer.validated_data['installment_param_id']
        category_id = request.data.get('category_id')  # انتظار داریم category_id از سمت کلاینت بیاد

        try:
            param = CompanyInstallmentParameter.objects.get(pk=installment_param_id)
        except CompanyInstallmentParameter.DoesNotExist:
            return Response({'error': 'پارامتر اقساط شرکتی یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        # بررسی دسته‌بندی مجاز
        if param.categories.exists():
            if not category_id:
                return Response({'error': 'دسته‌بندی محصول مشخص نشده است.'}, status=status.HTTP_400_BAD_REQUEST)
            if not param.categories.filter(pk=category_id).exists():
                return Response({'error': 'این روش اقساطی برای این دسته‌بندی قابل استفاده نیست.'}, status=status.HTTP_400_BAD_REQUEST)

        # محاسبه اقساط
        result = calculate_company_installment(product_price, down_payment, param)
        checks = generate_company_checks(result['monthly_payment'], result['repayment_period'])

        return Response({
            "increased_price": result['increased_price'],
            "remaining_price": result['remaining_price'],
            "monthly_payment": result['monthly_payment'],
            "total_interest": result['total_interest'],
            "repayment_period": result['repayment_period'],
            "checks": checks,
        })

