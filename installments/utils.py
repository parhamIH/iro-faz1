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
