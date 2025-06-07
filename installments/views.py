from decimal import Decimal, ROUND_HALF_UP
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
    def post(self, request):
        serializer = InstallmentCalculationInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        product_price = Decimal(str(data['product_price']))
        down_payment = Decimal(str(data['down_payment']))
        param = get_object_or_404(InstallmentParameter, pk=data['installment_param_id'])

        # تبدیل درصدها به Decimal
        initial_increase_percent = Decimal(str(param.initial_increase_percent))
        post_down_payment_increase_percent = Decimal(str(param.post_down_payment_increase_percent))
        bank_tax_interest_percent = Decimal(str(param.bank_tax_interest_percent))

        # مرحله ۱: افزایش اولیه
        increased_price = product_price + (product_price * initial_increase_percent / Decimal("100"))

        # مرحله ۲: بعد از پیش‌پرداخت
        remaining_price = increased_price - down_payment

        # مرحله ۳: افزایش بعد از پیش‌پرداخت
        post_increased_price = remaining_price * (Decimal("1") + post_down_payment_increase_percent / Decimal("100"))

        # نرخ بهره ماهانه
        monthly_interest_rate = (bank_tax_interest_percent / Decimal("100")) / Decimal("12")

        final_loan_amount = post_increased_price

        # محاسبه اقساط
        loan_results = calculate_loan_payments(final_loan_amount, monthly_interest_rate, param.repayment_period)

        # تاریخ سررسید چک
        check_due_date = date.today() + timedelta(days=param.check_guarantee_period * 30)
        jdate = jdatetime.date.fromgregorian(date=check_due_date)
        jdate_str_fa = convert_to_persian_digits(jdate.strftime("%Y/%m/%d"))

        # محاسبه مبلغ ضمانت
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
def calculate_company_installment(product_price: Decimal, down_payment: Decimal, param) -> dict:
    # اطمینان از Decimal بودن ورودی‌ها
    product_price = Decimal(product_price)
    down_payment = Decimal(down_payment)
    monthly_interest_percent = Decimal(param.monthly_interest_percent)  # سود ماهیانه درصدی
    repayment_period = int(param.repayment_period)  # مدت بازپرداخت (ماه)

    # تبدیل درصد به عدد کسری
    monthly_interest_rate = monthly_interest_percent / Decimal("100")

    # سود کل: درصد ماهانه × مبلغ کالا × تعداد ماه
    total_interest = product_price * monthly_interest_rate * repayment_period

    # قیمت افزایش یافته کالا (اصل + سود کل)
    increased_price = product_price + total_interest

    # مبلغ باقی مانده پس از پیش پرداخت
    remaining_price = increased_price - down_payment

    # مبلغ هر قسط
    monthly_payment = remaining_price / repayment_period if repayment_period > 0 else Decimal('0')

    # گرد کردن اعداد به دو رقم اعشار
    increased_price = increased_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    remaining_price = remaining_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    monthly_payment = monthly_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_interest = total_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return {
        "increased_price": increased_price,
        "remaining_price": remaining_price,
        "monthly_payment": monthly_payment,
        "total_interest": total_interest,
        "repayment_period": repayment_period,
    }
