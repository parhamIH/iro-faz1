from rest_framework import serializers


class InstallmentCalculationInputSerializer(serializers.Serializer):
    product_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    down_payment = serializers.DecimalField(max_digits=12, decimal_places=2)
    product_id = serializers.IntegerField(required=False, help_text="آی‌دی محصول (اختیاری). اگر وارد نشود، از تنظیمات پیش‌فرض استفاده می‌شود.")


class CompanyInstallmentCalculationInputSerializer(serializers.Serializer):
    product_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    down_payment = serializers.DecimalField(max_digits=12, decimal_places=2)
    product_id = serializers.IntegerField(required=False, help_text="آی‌دی محصول (اختیاری). اگر وارد نشود، از تنظیمات پیش‌فرض استفاده می‌شود.")
