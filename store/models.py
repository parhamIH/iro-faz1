from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

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
# Create your models here.
class InstallmentPlan(models.Model):
    title = models.CharField(max_length=100)
    months = models.PositiveIntegerField()
    monthly_price = models.DecimalField(max_digits=12, decimal_places=2)
    discounts = models.ManyToManyField('Discount', related_name='installment_plans', blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.months} ماهه ({self.monthly_price} تومان)"




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
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return self.name

