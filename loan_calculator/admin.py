from django.contrib import admin
from .models import  LoanCondition, PrePaymentInstallment


class PrePaymentInstallmentInline(admin.TabularInline):
    model = PrePaymentInstallment
    extra = 1 # تعداد فرم‌های خالی برای افزودن قسط جدید
    ordering = ('order',)

@admin.register(LoanCondition)
class LoanConditionAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'product',
        'condition_type',
        'condition_months', 
        'annual_interest_rate_percent', 
        'initial_increase_percent',
        'secondary_increase_percent',
        'guarantee_type', 
        'has_guarantor',
        'delivery_days',
    )
    list_filter = ('condition_type', 'guarantee_type', 'has_guarantor', 'product')
    search_fields = ('title', 'product__name')
    inlines = [PrePaymentInstallmentInline] # اضافه کردن امکان تعریف اقساط پیش‌پرداخت در همان صفحه

@admin.register(PrePaymentInstallment)
class PrePaymentInstallmentAdmin(admin.ModelAdmin):
    list_display = (
        'loan_condition',
        'order',
        'percent_of_initial_increased_price',
        'days_offset_for_payment',
        'due_date_from_today'
    )
    list_filter = ('loan_condition__product', 'loan_condition__condition_type')
    search_fields = ('loan_condition__title',)
    ordering = ('loan_condition', 'order') 