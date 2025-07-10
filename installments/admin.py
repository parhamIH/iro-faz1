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
        'get_categories',  # 🔹 نمایش دسته‌بندی‌ها
    )
    filter_horizontal = ('applicable_categories',)

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.applicable_categories.all()])
    get_categories.short_description = "دسته‌بندی‌ها"


@admin.register(CompanyInstallmentParameter)
class CompanyInstallmentParameterAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'repayment_period',
        'monthly_interest_percent',
        'minimum_down_payment',
        'guarantee_method',
        'get_categories',  # 🔹 نمایش دسته‌بندی‌ها
    )
    filter_horizontal = ('applicable_categories',)

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.applicable_categories.all()])
    get_categories.short_description = "دسته‌بندی‌ها"
