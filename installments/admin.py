from django.contrib import admin
from .models import InstallmentParameter, CompanyInstallmentParameter

@admin.register(InstallmentParameter)
class InstallmentParameterAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'repayment_period',
        'initial_increase_percent',
        'check_guarantee_period',
        'minimum_down_payment',
        'post_down_payment_increase_percent',
        'bank_tax_interest_percent',
        'method',
    )
filter_horizontal = ('categories',)    

@admin.register(CompanyInstallmentParameter)
class CompanyInstallmentParameterAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'repayment_period',
        'monthly_interest_percent',
        'minimum_down_payment',
        'guarantee_method',
    )
filter_horizontal = ('categories',)    