# installments/utils.py

import math

def calculate_loan_payments(loan_price, monthly_interest_rate, return_months):
    if monthly_interest_rate == 0:
        monthly_payment = loan_price / return_months
    else:
        monthly_payment = (
            loan_price
            * monthly_interest_rate
            * (1 + monthly_interest_rate) ** return_months
            / ((1 + monthly_interest_rate) ** return_months - 1)
        )
    total_payment = monthly_payment * return_months
    total_interest = total_payment - loan_price

    return {
        "monthly_payment": math.ceil(monthly_payment),
        "total_payment": math.ceil(total_payment),
        "total_interest": math.ceil(total_interest),
    }
