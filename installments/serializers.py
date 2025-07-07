# from rest_framework import serializers


# class InstallmentCalculationInputSerializer(serializers.Serializer):
#     product_price = serializers.DecimalField(
#         max_digits=12, decimal_places=2, help_text="قیمت محصول"
#     )
#     down_payment = serializers.DecimalField(
#         max_digits=12, decimal_places=2, help_text="پیش‌پرداخت"
#     )
#     installment_param_id = serializers.IntegerField(
#         help_text="شناسه تنظیمات قسط بانکی یا چکی"
#     )


# class CompanyInstallmentCalculationInputSerializer(serializers.Serializer):
#     product_price = serializers.DecimalField(
#         max_digits=12, decimal_places=2, help_text="قیمت محصول"
#     )
#     down_payment = serializers.DecimalField(
#         max_digits=12, decimal_places=2, help_text="پیش‌پرداخت"
#     )
#     installment_param_id = serializers.IntegerField(
#         help_text="شناسه تنظیمات قسط شرکتی"
#     )

from rest_framework import serializers

from rest_framework import serializers

class InstallmentCalculationInputSerializer(serializers.Serializer):
    product_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    down_payment = serializers.DecimalField(max_digits=12, decimal_places=2)
    installment_param_id = serializers.IntegerField(help_text="آی‌دی تنظیمات قسط بانکی")
    category_id = serializers.IntegerField(required=False, help_text="آی‌دی دسته‌بندی محصول (اختیاری)")  # اضافه شده
  



class CompanyInstallmentCalculationInputSerializer(serializers.Serializer):
    product_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    down_payment = serializers.DecimalField(max_digits=12, decimal_places=2)
    installment_param_id = serializers.IntegerField(help_text="آی‌دی تنظیمات اقساط شرکتی")
    category_id = serializers.IntegerField(required=False, help_text="آی‌دی دسته‌بندی محصول (اختیاری)")  # اضافه شده
