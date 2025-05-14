from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from colorfield.fields import ColorField


# Cfrom django.db import models

#need to add image to category
class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category, related_name='products')
    base_price_cash = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    installment_plans = models.ManyToManyField('InstallmentPlan', related_name='products', blank=True)
    discounts = models.ManyToManyField('Discount', related_name='products', blank=True)


    def __str__(self):
        return self.title

class Feature(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

from decimal import Decimal

class InstallmentPlan(models.Model):
    title = models.CharField(max_length=100)

    SELECT_MONTHS = [
        (12, "سالانه"),
        (18, "یک و نیم ساله"),
        (24, "دو ساله"),
        (36, "سه ساله")
    ]

    INTEREST_RATES = {
        12: 16,
        18: 34,
        24: 34,
        36: 43
    }

    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    months = models.PositiveIntegerField(choices=SELECT_MONTHS)
    prepayment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discounts = models.ManyToManyField('Discount', related_name='installment_plans', blank=True)

    def get_interest_rate(self):
        return self.INTEREST_RATES.get(self.months, 0)

    def calculate_financing_amount(self):
        base_price = self.product.base_price_cash + (self.product.base_price_cash * Decimal("0.05"))
        remaining = base_price - self.prepayment
        rate = self.get_interest_rate()
        increase = remaining * Decimal(rate) / 100
        return remaining + increase

    def calculate_monthly_installment(self):
        return self.calculate_financing_amount() / self.months

    def total_payment(self):
        return self.calculate_financing_amount()

    def estimated_cash_price(self):
        rate = self.get_interest_rate()
        if rate == 0:
            return self.total_payment()
        return self.total_payment() / (1 + (rate * self.months / 100))

    def __str__(self):
        return f"{self.title} - {self.months} ماهه - قسط: {self.calculate_monthly_installment():,.0f} تومان (سود: {self.get_interest_rate()}%)"

class ProductFeatureValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feature_values')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product.title} - {self.feature.name}: {self.value}"

class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    color = models.ForeignKey('Color', on_delete=models.CASCADE, related_name='options', blank=True, null=True)
    price_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.title} - {self.feature.name}: {self.value} (+{self.price_change})"


class Discount(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.PositiveIntegerField(
        help_text="درصد تخفیف",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    start_date = models.DateTimeField(
        validators=[MinValueValidator(timezone.now)] 
    )
    end_date = models.DateTimeField()

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({'end_date': "تاریخ پایان باید بعد از تاریخ شروع باشد."})

    @property
    def is_active(self):
        return self.start_date <= timezone.now() <= self.end_date

    def __str__(self):
        return f"{self.name} - {self.percentage}%"
class Gallery(models.Model):
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='product_gallery/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"عکس برای {self.product.title}"

class Color(models.Model):
    COLOR_PALETTE = [
        ("#FFFFFF", "white"),
        ("#000000", "black"),
        ("#FF0000", "red"),
        ("#008000", "green"),
        ("#0000FF", "blue"),
    ]
    name = models.CharField(max_length=50, verbose_name= "نام رنگ")
    hex_code = ColorField(samples=COLOR_PALETTE,max_length=7, verbose_name= "کد هگز رنگ",help_text=" مثال: #FFFFFF")

    class Meta:
        verbose_name = "رنگ"
        verbose_name_plural = "رنگ ها"
    
    def __str__(self):
        return self.name
