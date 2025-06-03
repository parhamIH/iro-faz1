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

    def __str__(self):
        return f"{self.get_method_display()} - {self.repayment_period} ماه - {self.initial_increase_percent}% اولیه"
