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
    description = models.TextField(blank=True, null=True)#delete able 
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
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

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
#delete discount from product and add it  to product-option
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True,allow_unicode=True,blank=True,null=True)
    categories = models.ManyToManyField(Category, related_name='products')
    feature = models.ManyToManyField("Feature", verbose_name=("ویژگی ها"))
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True, related_name='products') 
    is_active = models.BooleanField(default=True)


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
class Feature(models.Model):# delete able 
    name = models.CharField(max_length=255, verbose_name='نام ویژگی')
    value = models.CharField(max_length=255, verbose_name='مقدار ویژگی')
    is_main_feature = models.BooleanField(default=False, verbose_name='ویژگی اصلی')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                               related_name='features', verbose_name='دسته‌بندی')

    def __str__(self):
        try:
            category_name = self.category.name
        except:
            category_name = "دسته‌بندی تعریف‌نشده"
        status = 'ویژگی اصلی' if self.is_main_feature else 'ویژگی عمومی'
        return f"{category_name} | {self.name} = {self.value} ({status})"

class Specification(models.Model):
    DATA_TYPE_CHOICES = [
        ('int', 'عدد صحیح'),
        ('decimal', 'عدد اعشاری'),
        ('str', 'متن'),
        ('bool', 'بله/خیر'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='spec_definitions', verbose_name='دسته‌بندی')
    name = models.CharField(max_length=100, verbose_name='نام مشخصه')
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, blank=True)
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES, verbose_name='نوع داده')
    unit = models.CharField(max_length=30, blank=True, null=True, verbose_name='واحد')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
            counter = 1
            while Specification.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.name, allow_unicode=True)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} - {self.name} ({self.get_data_type_display()})"

    class Meta:
        verbose_name = 'مشخصه'
        verbose_name_plural = 'مشخصات'
        unique_together = ['category', 'name']

class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='spec_values', verbose_name='محصول')
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE, related_name='values', verbose_name='مشخصه')
    int_value = models.IntegerField(blank=True, null=True, verbose_name='مقدار عددی')
    decimal_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='مقدار اعشاری')
    str_value = models.CharField(max_length=255, blank=True, null=True, verbose_name='مقدار متنی')
    bool_value = models.BooleanField(blank=True, null=True, verbose_name='مقدار بله/خیر')

    def clean(self):
        # Ensure only one value field is set based on specification's data_type
        filled_values = [
            bool(self.int_value is not None),
            bool(self.decimal_value is not None),
            bool(self.str_value),
            bool(self.bool_value is not None)
        ]
        if sum(filled_values) > 1:
            raise ValidationError('فقط یک نوع مقدار می‌تواند پر شود')
        
        # Validate value matches specification's data_type
        if self.specification.data_type == 'int' and self.int_value is None:
            raise ValidationError('برای مشخصه عددی صحیح باید مقدار عددی وارد شود')
        elif self.specification.data_type == 'decimal' and self.decimal_value is None:
            raise ValidationError('برای مشخصه اعشاری باید مقدار اعشاری وارد شود')
        elif self.specification.data_type == 'str' and not self.str_value:
            raise ValidationError('برای مشخصه متنی باید مقدار متنی وارد شود')
        elif self.specification.data_type == 'bool' and self.bool_value is None:
            raise ValidationError('برای مشخصه بله/خیر باید مقدار بله/خیر وارد شود')

    def value(self):
        """Return the appropriate value based on specification's data_type"""
        if self.specification.data_type == 'int':
            return self.int_value
        elif self.specification.data_type == 'decimal':
            return self.decimal_value
        elif self.specification.data_type == 'str':
            return self.str_value
        elif self.specification.data_type == 'bool':
            return self.bool_value
        return None

    def __str__(self):
        value = self.value()
        unit = f" {self.specification.unit}" if self.specification.unit else ""
        return f"{self.product.title} - {self.specification.name}: {value}{unit}"

    class Meta:
        verbose_name = 'مقدار مشخصه محصول'
        verbose_name_plural = 'مقادیر مشخصات محصول'
        unique_together = ['product', 'specification']

#add  add provider for product-option foreignkey for faz 2 
class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')
    color = models.ForeignKey('Color', on_delete=models.CASCADE, related_name='options', blank=True, null=True)
    option_price = models.PositiveIntegerField(help_text="قیمت به تومان برای محصول با این ویژگی")
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    # Discount fields
    is_active_discount = models.BooleanField(default=False)
    discount = models.PositiveIntegerField(
        help_text="درصد تخفیف",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True
    )
    discount_start_date = models.DateTimeField(null=True, blank=True)
    discount_end_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        super().clean()
        if self.is_active_discount and self.discount_start_date and self.discount_end_date:
            if self.discount_end_date <= self.discount_start_date:
                raise ValidationError({'discount_end_date': "تاریخ پایان تخفیف باید بعد از تاریخ شروع باشد."})

    @property
    def is_discount_active(self):
        """Check if the discount is currently active"""
        if not self.is_active_discount or not self.discount:
            return False
        now = timezone.now()
        if self.discount_start_date and self.discount_end_date:
            return self.discount_start_date <= now <= self.discount_end_date
        return True

    def get_discount_amount(self):
        """Calculate the discount amount in Toman"""
        if not self.is_discount_active:
            return 0
        return int(self.option_price * (self.discount / 100))

    def get_final_price(self):
        """Get the final price after applying discount"""
        if not self.is_discount_active:
            return self.option_price
        return self.option_price - self.get_discount_amount()

    def set_discount_by_amount(self, discount_amount):
        """Set discount percentage based on a specific amount in Toman"""
        if discount_amount >= self.option_price:
            raise ValidationError("مبلغ تخفیف نمی‌تواند بیشتر یا مساوی قیمت محصول باشد.")
        self.discount = int((discount_amount / self.option_price) * 100)
        self.is_active_discount = True

    def set_discount_by_percentage(self, percentage):
        """Set discount by percentage (0-100)"""
        if not 0 <= percentage <= 100:
            raise ValidationError("درصد تخفیف باید بین 0 تا 100 باشد.")
        self.discount = percentage
        self.is_active_discount = True

    def __str__(self):
        base_str = f"{self.product.title} - (+{self.option_price})"
        if self.is_discount_active:
            return f"{base_str} (تخفیف: {self.discount}%)"
        return base_str

class Gallery(models.Model):
    product = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='product_gallery/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"عکس برای {self.product.product.title} - {self.product.color.name if self.product.color else 'بدون رنگ'}"

class Color(models.Model):
    COLOR_PALETTE = [
        ("#FFFFFF", "white"),
        ("#000000", "black"),
        ("#FF0000", "red"),
        ("#008000", "green"),
        ("#0000FF", "blue"),
    ]
    name = models.CharField(max_length=50, verbose_name= "نام رنگ" , unique=True)
    hex_code = ColorField(samples=COLOR_PALETTE,max_length=7, verbose_name= "کد هگز رنگ",help_text=" مثال: #FFFFFF")

    class Meta:
        verbose_name = "رنگ"
        verbose_name_plural = "colors"
    
    def __str__(self):
        return self.name
