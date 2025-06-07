from decimal import Decimal, ROUND_HALF_UP, getcontext

# تنظیم دقت کلی برای Decimal
getcontext().prec = 28

def calculate_loan_payments(loan_price: Decimal, monthly_interest_rate: Decimal, return_months: int) -> dict:
    """
    محاسبه قسط ماهانه، کل پرداختی و کل سود با استفاده از Decimal برای دقت مالی بالا.
    """
    # اطمینان از اینکه ورودی‌ها Decimal هستند
    loan_price = Decimal(loan_price)
    monthly_interest_rate = Decimal(monthly_interest_rate)

    if monthly_interest_rate == 0:
        monthly_payment = loan_price / Decimal(return_months)
    else:
        one_plus_r = (Decimal('1') + monthly_interest_rate)
        numerator = loan_price * monthly_interest_rate * (one_plus_r ** return_months)
        denominator = (one_plus_r ** return_months) - Decimal('1')
        monthly_payment = numerator / denominator

    monthly_payment = monthly_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_payment = (monthly_payment * return_months).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_interest = (total_payment - loan_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return {
        "monthly_payment": monthly_payment,
        "total_payment": total_payment,
        "total_interest": total_interest,
    }




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
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import jdatetime

def to_persian_number(input_str):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    return ''.join(persian_digits[int(ch)] if ch.isdigit() else ch for ch in str(input_str))

def to_persian_currency(amount: Decimal) -> str:
    formatted = f"{int(amount):,}"
    return to_persian_number(formatted)

def generate_company_checks(monthly_payment: Decimal, repayment_period: int) -> list:
    checks_info = []
    today = datetime.today()
    number_of_checks = (repayment_period + 1) // 2
    check_amount = (monthly_payment * 2).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    for i in range(number_of_checks):
        if i == 0:
            due_date = today + timedelta(days=45)
        else:
            due_date = due_date + timedelta(days=60)

        due_date_jalali = jdatetime.date.fromgregorian(date=due_date.date())
        date_str = due_date_jalali.strftime('%Y/%m/%d')
        date_str = to_persian_number(date_str)

        checks_info.append(
            f"چک شماره {to_persian_number(i + 1)} به مبلغ {to_persian_currency(check_amount)} ریال در تاریخ {date_str}"
        )

    return checks_info
