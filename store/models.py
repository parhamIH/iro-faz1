from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from colorfield.fields import ColorField
from django.utils.text import slugify
import random
from decimal import Decimal



class Brand (models.Model): 
    name = models.CharField(max_length=100) 
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
            counter = 1
            while Brand.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.name, allow_unicode=True)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

#need to add image to category
class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True, related_name='categories')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
            counter = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.name, allow_unicode=True)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name 

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        blank=True,
        null=True
    )
    categories = models.ManyToManyField(Category, related_name='products')
    base_price_cash = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    installment_plans = models.ManyToManyField('InstallmentPlan', related_name='products', blank=True)
    discounts = models.ManyToManyField('Discount', related_name='products', blank=True) # need to add discount to product and add discount to product option
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True, related_name='products')

    def save(self, *args, **kwargs):
        if not self.slug:
            # Create a simple slug from the title
            base_slug = slugify(self.title, allow_unicode=True)
            
            # If slug exists, append a number
            counter = 1
            new_slug = base_slug
            while Product.objects.filter(slug=new_slug).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = new_slug
                
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
class Feature(models.Model):
    FEATURE_TYPES = [
        ('technical', 'مشخصات فنی'),
        ('physical', 'مشخصات فیزیکی'),
        ('general', 'مشخصات عمومی'),
    ]

    name = models.CharField(max_length=100, verbose_name="نام ویژگی")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                                 related_name='features', verbose_name="دسته‌بندی")
    type = models.CharField(max_length=20, choices=FEATURE_TYPES, default='general', 
                            verbose_name="نوع ویژگی")
    unit = models.CharField(max_length=50, blank=True, null=True, verbose_name="واحد اندازه‌گیری")
    is_main_feature = models.BooleanField(default=False, verbose_name="ویژگی اصلی")
    display_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        unique_together = ['name', 'category']  # نام ویژگی در هر دسته منحصربه‌فرد باشد
        ordering = ['display_order', 'name']
        verbose_name = 'تعریف ویژگی'
        verbose_name_plural = 'تعریف ویژگی‌ها'

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class InstallmentPlan(models.Model): #need to delete ? ? ?
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

class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                                related_name='features', verbose_name="محصول")
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, 
                                verbose_name="ویژگی")
    value = models.CharField(max_length=255, verbose_name="مقدار ویژگی")
    value_numeric = models.DecimalField(max_digits=10, decimal_places=2, 
                                        null=True, blank=True, verbose_name="مقدار عددی")

    class Meta:
        unique_together = ['product', 'feature']  # یک ویژگی برای هر محصول تنها یکبار باشد
        ordering = ['feature__display_order']
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی‌های محصول'

    def clean(self):
        from decimal import Decimal, DecimalException
        # اگر ویژگی دارای واحد تعریف شده است، تلاش می‌کنیم مقدار عددی استخراج شود
        if self.feature.unit and self.value_numeric is None:
            try:
                self.value_numeric = Decimal(self.value.split()[0])
            except (ValueError, IndexError, DecimalException):
                raise ValidationError({'value': 'برای ویژگی‌های دارای واحد، مقدار باید عددی باشد.'})

    def __str__(self):
        if self.feature.unit:
            return f"{self.product.name} - {self.feature.name}: {self.value} {self.feature.unit}"
        return f"{self.product.name} - {self.feature.name}: {self.value}"

class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    color = models.ForeignKey('Color', on_delete=models.CASCADE, related_name='options', blank=True, null=True)
    option_price = models.PositiveIntegerField(help_text="قیمت به تومان برای محصول با این ویژگی")

    def __str__(self):
        return f"{self.product.title} - {self.feature.name}: {self.value} (+{self.option_price})"


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
    
    product = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='product_gallery/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"عکس برای {self.product.product.title}"

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
        verbose_name_plural = "colors"
    
    def __str__(self):
        return self.name
