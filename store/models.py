from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from colorfield.fields import ColorField
from django.utils.text import slugify
import random
from mptt.models import MPTTModel, TreeForeignKey
from . import models as installments 


#public__________________________________________ ------warranty------ _______________________________________

class Warranty(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام گارانتی')
    company = models.CharField(max_length=100, verbose_name='شرکت ارائه دهنده', blank=True, null=True)
    duration = models.PositiveIntegerField(verbose_name='مدت گارانتی (ماه)', help_text='مدت زمان گارانتی به ماه')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    terms_conditions = models.TextField(verbose_name='شرایط و ضوابط', blank=True)
    support_phone = models.CharField(max_length=20, verbose_name='شماره تماس پشتیبانی', blank=True)
    registration_required = models.BooleanField(default=False, verbose_name='نیاز به ثبت گارانتی')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = 'گارانتی'
        verbose_name_plural = 'گارانتی‌ها'
        ordering = ['name']

    def __str__(self):
        return f"{self.company} - {self.name} - {self.duration} ماه"

#public__________________________________________ ------tag------ _______________________________________

class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام تگ')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True, verbose_name='شناسه URL')

    class Meta:
        verbose_name = 'تگ'
        verbose_name_plural = 'تگ‌ها'

    def __str__(self):
        return self.name


#public__________________________________________ ------brand------ _______________________________________
class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True)

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'

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



#Category__________________________________________ ------category------ _______________________________________

class Category(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    brand = models.ManyToManyField('Brand', blank=True, related_name='categories')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.ImageField(upload_to='categories/icons/', blank=True, null=True)
    class MPTTMeta:
        order_insertion_by = ["parent", "name"]

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'

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



#product__________________________________________ ------product------ _______________________________________
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='products')
    specifications = models.ManyToManyField("Specification", through='ProductSpecification', verbose_name="مشخصات")
    tags = models.ManyToManyField('Tag', related_name='products')
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True, related_name='products')
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            counter = 1
            new_slug = base_slug
            while Product.objects.filter(slug=new_slug).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = new_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
#Specification__________________________________________ ------specification group  ------ _______________________________________   

class SpecificationGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام گروه مشخصات')
    
    class Meta:
        verbose_name = 'گروه مشخصات'
        verbose_name_plural = 'گروه‌های مشخصات'

    def __str__(self):
        return self.name

#Specification__________________________________________ ------specification------ _______________________________________   
class Specification(models.Model):
    DATA_TYPE_CHOICES = [
        ('int', 'عدد صحیح'),
        ('decimal', 'عدد اعشاری'),
        ('str', 'متن'),
        ('bool', 'بله/خیر'),
    ]

    categories = models.ManyToManyField(Category, related_name='spec_definitions', verbose_name='دسته‌بندی‌ها')

    group = models.ForeignKey(SpecificationGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='specifications', verbose_name='گروه مشخصات')

    name = models.CharField(max_length=100, verbose_name='نام مشخصه')
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, blank=True)
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES, verbose_name='نوع داده')
    unit = models.CharField(max_length=30, blank=True, null=True, verbose_name='واحد')
    is_main = models.BooleanField(default=False, verbose_name='مشخصه اصلی', help_text='مشخصه اصلی برای محصولات است')

    class Meta:
        verbose_name = 'مشخصه'
        verbose_name_plural = 'مشخصات'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
            counter = 1
            while Specification.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.name, allow_unicode=True)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        categories_names = ", ".join(cat.name for cat in self.categories.all())
        return f"{categories_names} - {self.name} ({self.get_data_type_display()})"

#product__________________________________________ ------product specification------ _______________________________________
class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='spec_values', verbose_name='محصول')
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE, related_name='values', verbose_name='مشخصه')
    int_value = models.IntegerField(blank=True, null=True, verbose_name='مقدار عددی')
    decimal_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='مقدار اعشاری')
    str_value = models.CharField(max_length=255, blank=True, null=True, verbose_name='مقدار متنی')
    bool_value = models.BooleanField(blank=True, null=True, verbose_name='مقدار بله/خیر')
    is_main = models.BooleanField(default=False, verbose_name='مشخصه اصلی', help_text='مشخصه اصلی برای محصول است')

    class Meta:
        verbose_name = 'مقدار مشخصه محصول'
        verbose_name_plural = 'مقادیر مشخصات محصول'
        unique_together = ['product', 'specification']

    def clean(self):
        if self.specification.data_type == 'int' and self.int_value is None:
            raise ValidationError('برای مشخصه عددی صحیح باید مقدار عددی وارد شود')
        elif self.specification.data_type == 'decimal' and self.decimal_value is None:
            raise ValidationError('برای مشخصه اعشاری باید مقدار اعشاری وارد شود')
        elif self.specification.data_type == 'str' and not self.str_value:
            raise ValidationError('برای مشخصه متنی باید مقدار متنی وارد شود')
        elif self.specification.data_type == 'bool' and self.bool_value is None:
            raise ValidationError('برای مشخصه بله/خیر باید مقدار بله/خیر وارد شود')

    def value(self):
        if self.specification.data_type == 'int':
            return self.int_value
        elif self.specification.data_type == 'decimal':
            return self.decimal_value
        elif self.specification.data_type == 'str':
            return self.str_value
        elif self.specification.data_type == 'bool':
            return self.bool_value
        return None

#add  add provider for product-option foreignkey for faz 2 
#product__________________________________________ ------product option------ _______________________________________
class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options', verbose_name='محصول')
    color = models.ForeignKey('Color', on_delete=models.CASCADE, related_name='options', blank=True, null=True, verbose_name='رنگ')
    option_price = models.PositiveIntegerField(help_text="قیمت به تومان برای محصول با این ویژگی", verbose_name='قیمت ویژگی')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=1, verbose_name='تعداد')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    warranty = models.ForeignKey(Warranty, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='گارانتی', related_name='product_options')

    is_active_discount = models.BooleanField(default=False, verbose_name='تخفیف فعال است؟')
    discount = models.PositiveIntegerField(help_text="درصد تخفیف",validators=[MinValueValidator(0), MaxValueValidator(100)],blank=True,null=True,verbose_name='درصد تخفیف')
    discount_start_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ شروع تخفیف')
    discount_end_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پایان تخفیف')

    class Meta:
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی‌های محصول'

    def clean(self):
        super().clean()
        if self.is_active_discount and self.discount_start_date and self.discount_end_date:
            if self.discount_end_date <= self.discount_start_date:
                raise ValidationError({'discount_end_date': "تاریخ پایان تخفیف باید بعد از تاریخ شروع باشد."})

    @property
    def is_discount_active(self):
        if not self.is_active_discount or not self.discount:
            return False
        now = timezone.now()
        if self.discount_start_date and self.discount_end_date:
            return self.discount_start_date <= now <= self.discount_end_date
        return True

    def get_discount_amount(self):
        if not self.is_discount_active:
            return 0
        return int(self.option_price * (self.discount / 100))

    def get_final_price(self):
        if not self.is_discount_active:
            return self.option_price
        return self.option_price - self.get_discount_amount()

    def set_discount_by_amount(self, discount_amount):
        if discount_amount >= self.option_price:
            raise ValidationError("مبلغ تخفیف نمی‌تواند بیشتر یا مساوی قیمت محصول باشد.")
        self.discount = int((discount_amount / self.option_price) * 100)
        self.is_active_discount = True

    def set_discount_by_percentage(self, percentage):
        if not 0 <= percentage <= 100:
            raise ValidationError("درصد تخفیف باید بین 0 تا 100 باشد.")
        self.discount = percentage
        self.is_active_discount = True

    def change_activity(self):
        self.is_active = self.quantity >= 1

    def __str__(self):
        base_str = f"{self.product.title} - (+{self.option_price})"
        if self.is_discount_active:
            return f"{base_str} (تخفیف: {self.discount}%)"
        return base_str

#product__________________________________________ ------Gallery------ _______________________________________

class Gallery(models.Model):
    product = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_name='gallery', verbose_name='ویژگی محصول')
    image = models.ImageField(upload_to='product_gallery/', verbose_name='تصویر')
    alt_text = models.CharField(max_length=255, blank=True, verbose_name='متن جایگزین')

    class Meta:
        verbose_name = 'گالری تصویر'
        verbose_name_plural = 'گالری تصاویر'

    def __str__(self):
        color_name = self.product.color.name if self.product.color else 'بدون رنگ'
        return f"عکس برای {self.product.product.title} - {color_name}"


#public__________________________________________ ------color------ _______________________________________
class Color(models.Model):
    COLOR_PALETTE = [
        ("#FFFFFF", "white"),
        ("#000000", "black"),
        ("#FF0000", "red"),
        ("#008000", "green"),
        ("#0000FF", "blue"),
    ]
    name = models.CharField(max_length=50, verbose_name="نام رنگ", unique=True)
    hex_code = ColorField(samples=COLOR_PALETTE, max_length=7, verbose_name="کد هگز رنگ", help_text="مثال: #FFFFFF")

    class Meta:
        verbose_name = "رنگ"
        verbose_name_plural = "رنگ‌ها"

    def __str__(self):
        return self.name

# Articles__________________________________________ ------ArticleCategory------ _______________________________________

class ArticleCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام دسته‌بندی')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True)

    class Meta:
        verbose_name = 'دسته‌بندی مقاله'
        verbose_name_plural = 'دسته‌بندی‌های مقاله'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
            counter = 1
            while ArticleCategory.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.name, allow_unicode=True)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


#Articles __________________________________________ ------Article------ _______________________________________

class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name='عنوان')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True, verbose_name='تگ‌ها')
    content = models.TextField(verbose_name='محتوا')
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name='تصویر')
    category = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE, related_name='articles', verbose_name='دسته‌بندی')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    is_published = models.BooleanField(default=True, verbose_name='منتشر شده')

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            counter = 1
            new_slug = base_slug
            while Article.objects.filter(slug=new_slug).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = new_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title