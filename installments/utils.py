from decimal import Decimal, ROUND_HALF_UP, getcontext
from datetime import datetime, timedelta
import jdatetime

# تنظیم دقت کلی Decimal
getcontext().prec = 28


def calculate_loan_payments(loan_price: Decimal, monthly_interest_rate: Decimal, return_months: int) -> dict:
    """
    محاسبه اقساط بانکی یا چکی.
    """
    loan_price = Decimal(loan_price)
    monthly_interest_rate = Decimal(monthly_interest_rate)

    if monthly_interest_rate == 0:
        monthly_payment = loan_price / Decimal(return_months)
    else:
        one_plus_r = Decimal("1") + monthly_interest_rate
        numerator = loan_price * monthly_interest_rate * (one_plus_r ** return_months)
        denominator = (one_plus_r ** return_months) - Decimal("1")
        monthly_payment = numerator / denominator

    monthly_payment = monthly_payment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_payment = (monthly_payment * return_months).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_interest = (total_payment - loan_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "monthly_payment": monthly_payment,
        "total_payment": total_payment,
        "total_interest": total_interest,
    }


def calculate_company_installment(product_price: Decimal, down_payment: Decimal, param) -> dict:
    """
    محاسبه اقساط شرکتی.
    """
    product_price = Decimal(product_price)
    down_payment = Decimal(down_payment)
    monthly_interest_rate = Decimal(param.monthly_interest_percent) / Decimal("100")
    repayment_period = int(param.repayment_period)

    total_interest = product_price * monthly_interest_rate * repayment_period
    increased_price = product_price + total_interest
    remaining_price = increased_price - down_payment

    monthly_payment = remaining_price / repayment_period if repayment_period > 0 else Decimal("0")

    return {
        "increased_price": increased_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "remaining_price": remaining_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "monthly_payment": monthly_payment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "total_interest": total_interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "repayment_period": repayment_period,
    }


def to_persian_number(input_str):
    """
    تبدیل ارقام انگلیسی به فارسی
    """
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    return ''.join(persian_digits[int(ch)] if ch.isdigit() else ch for ch in str(input_str))


def to_persian_currency(amount: Decimal) -> str:
    """
    نمایش عدد به‌صورت ریال با جداکننده هزار و ارقام فارسی
    """
    formatted = f"{int(amount):,}"
    return to_persian_number(formatted)


def generate_company_checks(monthly_payment: Decimal, repayment_period: int) -> list:
    """
    تولید لیست چک‌های شرکتی، هر چک برای ۲ ماه، تاریخ جلالی و مبلغ به ریال و فارسی
    """
    checks_info = []
    today = datetime.today()
    number_of_checks = (repayment_period + 1) // 2
    check_amount = (monthly_payment * 2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    due_date = today + timedelta(days=45)  # تاریخ اولین چک

    for i in range(number_of_checks):
        due_date_jalali = jdatetime.date.fromgregorian(date=due_date.date())
        date_str = to_persian_number(due_date_jalali.strftime('%Y/%m/%d'))

        checks_info.append(
            f"چک شماره {to_persian_number(i + 1)} به مبلغ {to_persian_currency(check_amount)} ریال در تاریخ {date_str}"
        )

        due_date += timedelta(days=60)  # چک بعدی هر ۲ ماه یک بار

    return checks_info
