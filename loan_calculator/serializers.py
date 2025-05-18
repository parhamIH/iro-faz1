from rest_framework import serializers
from .models import LoanCondition, PrePaymentInstallment

class PrePaymentInstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrePaymentInstallment
        fields = ["id", "percent_of_initial_increased_price", "days_offset_for_payment", "order", "due_date_from_today"]
        ref_name = "loan_calculator_prepayment"

class LoanConditionSerializer(serializers.ModelSerializer):
    prepayment_installments = PrePaymentInstallmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = LoanCondition
        fields = ["id", "title", "condition_type", "product",
                 "guarantee_type", "has_guarantor", 
                 "condition_months", "annual_interest_rate_percent", 
                 "initial_increase_percent", "single_prepayment_percent",
                 "secondary_increase_percent", "delivery_days", "prepayment_installments"]
        ref_name = "loan_calculator_condition"
