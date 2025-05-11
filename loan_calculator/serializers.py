# from rest_framework import serializers
# from .models import Product, LoanCondition, PrePaymentInstallment

# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = '__all__'

# class PrePaymentInstallmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PrePaymentInstallment
#         fields = ('id', 'percent_of_initial_increased_price', 'days_offset_for_payment', 'order', 'due_date_from_today')

# class LoanConditionSerializer(serializers.ModelSerializer):
#     prepayment_installments = PrePaymentInstallmentSerializer(many=True, read_only=True)
#     # اگر می‌خواهید هنگام ایجاد/به‌روزرسانی LoanCondition بتوانید اقساط را هم بفرستید،
#     # باید یک سریالایزر قابل نوشتن برای PrePaymentInstallment داشته باشید و 
#     # متدهای create/update را در LoanConditionSerializer بازنویسی کنید.

#     class Meta:
#         model = LoanCondition
#         fields = '__all__' # یا فیلدهای مورد نظرتان را لیست کنید
#         read_only_fields = ('guarantor_status_display', 'delivery_title_display') 