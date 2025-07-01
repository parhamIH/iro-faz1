from django.db import models

from django.db import models

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
        help_text="نوع ضمانت (چک یا سفته)"
    )

    repayment_period = models.PositiveIntegerField(
        default=12,
        help_text="مدت بازپرداخت (بر حسب ماه)"
    )

    initial_increase_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=25.00,
        help_text="درصد افزایش اولیه (قبل از محاسبه پیش‌پرداخت)"
    )

    check_guarantee_period = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=13,
        help_text="مدت زمان ضمانت چک (ماه)"
    )

    minimum_down_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="حداقل مبلغ پیش‌پرداخت"
    )

    post_down_payment_increase_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        help_text="درصد افزایش قیمت پس از کسر پیش‌پرداخت"
    )

    bank_tax_interest_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="سود/مالیات بانکی (درصدی)"
    )

    # ⬇️ ارتباط با محصولات خاص
    products = models.ManyToManyField(
        'store.Product',
        blank=True,
        related_name='bank_installments',
        verbose_name='محصولات مجاز',
        help_text='اگر خالی باشد، برای همه محصولات فعال است.'
    )

    def __str__(self):
        return f"{self.get_method_display()} - {self.repayment_period} ماه - {self.initial_increase_percent}% اولیه"

from django.db import models

class CompanyInstallmentParameter(models.Model):
    repayment_period = models.PositiveIntegerField(
        default=12,
        help_text="مدت بازپرداخت (ماه)"
    )

    monthly_interest_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="سود ماهیانه (درصد)"
    )

    minimum_down_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="حداقل مبلغ پیش‌پرداخت"
    )

    guarantee_method = models.CharField(
        max_length=20,
        default='check',
        help_text="نوع ضمانت (مثلا چک، سفته و غیره)"
    )

    # ⬇️ ارتباط با محصولات خاص
    products = models.ManyToManyField(
        'store.Product',
        blank=True,
        related_name='company_installments',
        verbose_name='محصولات مجاز',
        help_text='اگر خالی باشد، برای همه محصولات فعال است.'
    )

    def __str__(self):
        return f"شرایط شرکتی - {self.repayment_period} ماه - سود ماهیانه {self.monthly_interest_percent}%"
