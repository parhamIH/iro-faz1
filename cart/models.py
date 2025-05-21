from django.db import models
from django.utils import timezone
import uuid
from accounts.models import ClientProfile
from store.models import ProductOption
from model_utils import FieldTracker
# Create your models here.

class Cart(models.Model):
    STATUS_CHOICES = [
        ('در حال انتظار', 'در حال انتظار'),
        ('در حال پردازش', 'در حال پردازش'),
        ('ارسال شده', 'ارسال شده'),
        ('تحویل داده شده', 'تحویل داده شده'),
        ('لغو شده', 'لغو شده'),
    ]

    user = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.user.username} - {self.created_date}"
    
    def total_price(self):
        """محاسبه مجموع قیمت همه آیتم‌های سبد خرید"""
        return sum(item.total_final_price for item in self.cartitem_set.all())

    def item_count(self):
        """تعداد کل آیتم‌های موجود در سبد خرید"""
        return self.cartitem_set.count()

    def total_items_quantity(self):
        """مجموع تعداد همه محصولات در سبد خرید"""
        return sum(item.count for item in self.cartitem_set.all())

    def clear(self):
        """پاک کردن همه آیتم‌های سبد خرید"""
        self.cartitem_set.all().delete()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    package = models.ForeignKey(ProductOption, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)
    final_price = models.PositiveIntegerField(null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_date']

    def save(self, *args, **kwargs):
        # اگر سبد پرداخت شده و قیمت نهایی هنوز ثبت نشده، قیمت جاری رو ذخیره کن
        if self.cart.is_paid and self.final_price is None:
            self.final_price = self.package.price
        super().save(*args, **kwargs)

    def get_price(self):
        """گرفتن قیمت: اگر پرداخت شده از final_price، وگرنه از قیمت جاری پکیج"""
        return self.final_price if self.final_price is not None else self.package.price

    def total_price(self):
        """قیمت کل بدون در نظر گرفتن ویژگی جدید"""
        return self.get_price() * self.count

    @property
    def total_final_price(self):
        """محاسبه قیمت نهایی ضربدر تعداد"""
        return self.get_price() * self.count

    def __str__(self):
        return f'{self.package.product.name} - {self.count} عدد'



class Order(models.Model):
    SHIPPING_CHOICES = [
        ('post', 'پست'),
        ('tipax', 'تیپاکس'),
        ('express', 'پیک موتوری'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('online', 'پرداخت آنلاین'),
        ('wallet', 'کیف پول'),
        ('cod', 'پرداخت در محل'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('پرداخت شده', 'پرداخت شده'),
        ('در انتظار پرداخت', 'در انتظار پرداخت'),
        ('در انتظار تایید', 'در انتظار تایید'),
        ('ناموفق', 'ناموفق'),
        ('لغو شده', 'لغو شده'),
    ]
    
    user = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT)
    address = models.ForeignKey('accounts.Address', on_delete=models.PROTECT)
    
    order_number = models.CharField(max_length=100, unique=True, editable=False, default=uuid.uuid4)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # شناسه پرداخت از درگاه
    payment_date = models.DateTimeField(null=True, blank=True)  # زمان پرداخت موفق
    payment_reference_id = models.CharField(max_length=100, blank=True, null=True)  # کد پیگیری پرداخت
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='در انتظار پرداخت',
        verbose_name='وضعیت پرداخت'
    )  # وضعیت پرداخت
    payment_error = models.TextField(blank=True, null=True)  # پیام خطای پرداخت
    
    status = models.CharField(max_length=20, choices=Cart.STATUS_CHOICES, default='در حال انتظار')
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_CHOICES, default='post')
    shipping_cost = models.PositiveIntegerField(default=0)
    total_price = models.PositiveIntegerField()
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.PositiveIntegerField(default=0)
    
    shipping_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)  # تاریخ تحویل انتخاب شده توسط کاربر
    jalali_delivery_date = models.CharField(max_length=50, blank=True, null=True)  # تاریخ تحویل شمسی
    
    notes = models.TextField(blank=True, null=True)
    
    # Add field tracker to track changes
    tracker = FieldTracker(fields=['status'])
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"
    
    def calculate_total(self):
        """محاسبه قیمت نهایی سفارش با در نظر گرفتن هزینه ارسال و تخفیف"""
        return self.cart.total_price() + self.shipping_cost - self.discount_amount
        
    def get_shipping_method_display_name(self):
        """نمایش نام فارسی روش ارسال"""
        shipping_methods = dict(self.SHIPPING_CHOICES)
        return shipping_methods.get(self.shipping_method, 'نامشخص')    

    def mark_as_paid(self):
        """علامت‌گذاری سفارش به عنوان پرداخت شده"""
        self.payment_status = 'پرداخت شده'
        self.payment_date = timezone.now()
        self.cart.is_paid = True
        self.cart.save()
        self.save()

    def is_cancelable(self):
        """بررسی امکان لغو سفارش"""
        return self.status in ['در حال انتظار', 'در حال پردازش']

    def cancel_order(self):
        """لغو سفارش"""
        if self.is_cancelable():
            self.status = 'لغو شده'
            self.save()
            return True
        return False

