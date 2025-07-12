from django.db import models
from django.utils import timezone
import uuid
from store.models import ProductOption
from model_utils import FieldTracker
from django.contrib.auth import get_user_model
<<<<<<< HEAD
=======
from decimal import Decimal
>>>>>>> 44326bdd00e41038f3f57ffbe53f1ba80f8e3880

User = get_user_model()

def generate_order_number():
    return str(uuid.uuid4())

class Cart(models.Model):
    STATUS_CHOICES = [
        ('در حال انتظار', 'در حال انتظار'),
        ('در حال پردازش', 'در حال پردازش'),
        ('ارسال شده', 'ارسال شده'),
        ('تحویل داده شده', 'تحویل داده شده'),
        ('لغو شده', 'لغو شده'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    is_paid = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.created_date}"
        return f"ناشناس - {self.session_key} - {self.created_date}"
    
    def total_price(self):
        """محاسبه مجموع قیمت همه آیتم‌های سبد خرید"""
        return sum(item.total_final_price for item in self.cartitem_set.all()) or Decimal('0.00')

    def item_count(self):
        """تعداد کل آیتم‌های موجود در سبد خرید"""
        return self.cartitem_set.count()

    def total_items_quantity(self):
        """مجموع تعداد همه محصولات در سبد خرید"""
        return sum(item.count for item in self.cartitem_set.all()) or 0

    def clear(self):
        """پاک کردن همه آیتم‌های سبد خرید"""
        self.cartitem_set.all().delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    package = models.ForeignKey(ProductOption, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_date']

    def save(self, *args, **kwargs):
        # اگر سبد پرداخت شده و قیمت نهایی هنوز ثبت نشده، قیمت نهایی فعلی پکیج را ذخیره کن
        if self.cart.is_paid and self.final_price is None:
            self.final_price = self.package.get_final_price()
        super().save(*args, **kwargs)

    def get_price(self):
        """گرفتن قیمت: اگر پرداخت شده از final_price، وگرنه از قیمت جاری پکیج"""
        return self.final_price if self.final_price is not None else self.package.get_final_price()

    def total_price(self):
        """قیمت کل بدون در نظر گرفتن ویژگی جدید"""
        return self.get_price() * self.count

    @property
    def total_final_price(self):
        """محاسبه قیمت نهایی ضربدر تعداد"""
        return self.get_price() * self.count

    def __str__(self):
<<<<<<< HEAD
        return f'{self.package.product.name} - {self.count} عدد'
=======
        return f'{self.package.product.title} - {self.count} عدد'

>>>>>>> 44326bdd00e41038f3f57ffbe53f1ba80f8e3880

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

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT)
    order_number = models.CharField(max_length=100, unique=True, editable=False, default=generate_order_number)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='در انتظار پرداخت')
    status = models.CharField(max_length=20, choices=Cart.STATUS_CHOICES, default='در حال انتظار')
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_CHOICES, default='post')
<<<<<<< HEAD
    shipping_cost = models.PositiveIntegerField(default=0)
    total_price = models.PositiveIntegerField(default=0)
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.PositiveIntegerField(default=0)
=======
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_price = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
>>>>>>> 44326bdd00e41038f3f57ffbe53f1ba80f8e3880
    shipping_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    jalali_delivery_date = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    tracker = FieldTracker(fields=['status'])

    def __str__(self):
        if self.user:
            return f"Order #{self.order_number} - {self.user.username}"
        else:
            return f"Order #{self.order_number} - ناشناس - {self.session_key}"

    def calculate_total_price(self):
        """محاسبه مجموع نهایی سفارش با در نظر گرفتن ارسال و تخفیف"""
        total = self.cart.total_price() + self.shipping_cost - self.discount_amount
<<<<<<< HEAD
        return max(total, 0)
=======
        return max(total, Decimal('0.00'))
>>>>>>> 44326bdd00e41038f3f57ffbe53f1ba80f8e3880

    def save(self, *args, **kwargs):
        # به روز رسانی قیمت کل هنگام ذخیره
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)
