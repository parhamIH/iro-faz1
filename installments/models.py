from django.db import models
from store.models import Category

class InstallmentParameter(models.Model):
    METHOD_CHECK = 'check'
    METHOD_PROMISSORY = 'promissory'
    METHOD_CHOICES = [
        (METHOD_CHECK, 'چک'),
        (METHOD_PROMISSORY, 'سفته'),
    ]

    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default=METHOD_CHECK,
        verbose_name='نوع ضمانت',
        help_text='نوع ضمانت (چک یا سفته)'
    )

    repayment_period = models.PositiveIntegerField(
        default=12,
        verbose_name='مدت بازپرداخت',
        help_text='مدت بازپرداخت (بر حسب ماه)'
    )

    initial_increase_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=25.00,
        verbose_name='درصد افزایش اولیه',
        help_text='درصد افزایش اولیه (قبل از محاسبه پیش‌پرداخت)'
    )

    check_guarantee_period = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=13,
        verbose_name='مدت ضمانت چک',
        help_text='مدت زمان ضمانت چک (ماه)'
    )

    minimum_down_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='حداقل پیش‌پرداخت',
        help_text='حداقل مبلغ پیش‌پرداخت'
    )

    post_down_payment_increase_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        verbose_name='درصد افزایش پس از پیش‌پرداخت',
        help_text='درصد افزایش قیمت پس از کسر پیش‌پرداخت'
    )

    bank_tax_interest_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='سود/مالیات بانکی',
        help_text='سود/مالیات بانکی (درصدی)'
    )

    applicable_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='bank_installment_params',
        verbose_name='دسته‌بندی‌های قابل اعمال',
        help_text='دسته‌بندی‌هایی که این روش قسطی بانکی روی آن‌ها اعمال می‌شود. اگر خالی باشد برای همه محصولات اعمال خواهد شد.'
    )

    class Meta:
        verbose_name = 'پارامتر قسط بانکی'
        verbose_name_plural = 'پارامترهای قسط بانکی'
        ordering = ['method', 'repayment_period']

    def __str__(self):
        return f"{self.get_method_display()} - {self.repayment_period} ماه - {self.initial_increase_percent}% افزایش اولیه"


class CompanyInstallmentParameter(models.Model):
    repayment_period = models.PositiveIntegerField(
        default=12,
        verbose_name='مدت بازپرداخت',
        help_text='مدت بازپرداخت (ماه)'
    )

    monthly_interest_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        verbose_name='سود ماهیانه',
        help_text='سود ماهیانه (درصد)'
    )

    minimum_down_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='حداقل پیش‌پرداخت',
        help_text='حداقل مبلغ پیش‌پرداخت'
    )

    guarantee_method = models.CharField(
        max_length=20,
        default='check',
        verbose_name='نوع ضمانت',
        help_text='نوع ضمانت (مثلا چک، سفته و غیره)'
    )

    applicable_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='company_installment_params',
        verbose_name='دسته‌بندی‌های قابل اعمال',
        help_text='دسته‌بندی‌هایی که این روش قسطی شرکتی روی آن‌ها اعمال می‌شود. اگر خالی باشد برای همه محصولات اعمال خواهد شد.'
    )

    class Meta:
        verbose_name = 'پارامتر قسط شرکتی'
        verbose_name_plural = 'پارامترهای قسط شرکتی'
        ordering = ['repayment_period']

    def __str__(self):
        return f"شرایط شرکتی - {self.repayment_period} ماه - سود ماهیانه {self.monthly_interest_percent}%"
