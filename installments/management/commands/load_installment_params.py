from django.core.management.base import BaseCommand
from installments.models import InstallmentParameter

class Command(BaseCommand):
    help = "بارگذاری داده‌های پیش‌فرض پارامترهای اقساط"

    def handle(self, *args, **kwargs):
        # حذف رکوردهای قبلی (اگر نیاز داری)
        InstallmentParameter.objects.all().delete()

        # داده‌های پیش‌فرض چک
        check_params = [
            InstallmentParameter(method=InstallmentParameter.METHOD_CHECK, period=12, increase_percent=25, check_period=13),
            InstallmentParameter(method=InstallmentParameter.METHOD_CHECK, period=18, increase_percent=34, check_period=6),
            InstallmentParameter(method=InstallmentParameter.METHOD_CHECK, period=24, increase_percent=34, check_period=6),
            InstallmentParameter(method=InstallmentParameter.METHOD_CHECK, period=36, increase_percent=43, check_period=6),
        ]

        # داده‌های پیش‌فرض برات
        promissory_params = [
            InstallmentParameter(method=InstallmentParameter.METHOD_PROMISSORY, period=4, increase_percent=5.5),
            InstallmentParameter(method=InstallmentParameter.METHOD_PROMISSORY, period=8, increase_percent=5.5),
            InstallmentParameter(method=InstallmentParameter.METHOD_PROMISSORY, period=10, increase_percent=5.5),
        ]

        # ذخیره در دیتابیس
        InstallmentParameter.objects.bulk_create(check_params + promissory_params)

        self.stdout.write(self.style.SUCCESS("پارامترهای اقساط اولیه با موفقیت بارگذاری شدند."))
