from rest_framework import serializers

class InstallmentCalculationInputSerializer(serializers.Serializer):
    product_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    down_payment = serializers.DecimalField(max_digits=12, decimal_places=2)
    installment_param_id = serializers.IntegerField(help_text="آی‌دی تنظیمات قسط")


class CompanyInstallmentCalculationInputSerializer(serializers.Serializer):
    product_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    down_payment = serializers.DecimalField(max_digits=12, decimal_places=2)
    installment_param_id = serializers.IntegerField(help_text="آی‌دی تنظیمات اقساط شرکتی")