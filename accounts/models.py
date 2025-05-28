from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator , MinLengthValidator 
from django.contrib.auth import get_user_model 
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from store.models import Product
from django.db.models.signals import post_save
from django.dispatch import receiver

def validate_iranian_national_id(national_id):
    """
    اعتبارسنجی کد ملی ایرانی
    
    شرایط کد ملی معتبر:
    1. دقیقاً 10 رقم باشد
    2. همه کاراکترها عدد باشند
    3. الگوریتم اعتبارسنجی کد ملی را پاس کند
    
    ساختار کد ملی:
    - 9 رقم اول: شماره اصلی
    - رقم دهم: رقم کنترلی
    """
    # بررسی طول کد ملی
    if not national_id or len(national_id) != 10:
        return False
    
    # بررسی عددی بودن تمام کاراکترها
    if not national_id.isdigit():
        return False
    
    # بررسی الگوی کدهای ملی غیرمعتبر مانند 0000000000 و 1111111111
    if national_id in ['0000000000', '1111111111', '2222222222', '3333333333', 
                      '4444444444', '5555555555', '6666666666', '7777777777', 
                      '8888888888', '9999999999']:
        return False
    
    # محاسبه رقم کنترلی
    check = int(national_id[9])
    sum_digits = 0
    
    for i in range(9):
        sum_digits += int(national_id[i]) * (10 - i)
    
    remainder = sum_digits % 11
    
    if remainder < 2:
        return check == remainder
    else:
        return check == 11 - remainder

def validate_national_id(value):
    if not validate_iranian_national_id(value):
        raise ValidationError(
            'کد ملی وارد شده معتبر نیست. کد ملی باید 10 رقم بوده و با الگوریتم صحیح کد ملی جمهوری اسلامی ایران مطابقت داشته باشد.'
        )

# Create your models here.


iran_phone_regex = RegexValidator(
    regex=r'^(?:\+98|0)?9\d{9}$',
    message="شماره تلفن باید با +98 یا 09 شروع شده و 11 رقم باشد (مثلاً: +989123456789 یا 09123456789)."
)


class CustomUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    

    # phone number 
    phone_number = models.CharField(max_length=13,validators=[iran_phone_regex],unique=True,blank=True,null=True,)
    is_phone_verified = models.BooleanField(default=False, verbose_name="تأیید شماره تلفن")
    verification_code = models.CharField(max_length=6, null=True, blank=True, verbose_name="کد تأیید")
    verification_code_created_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان ایجاد کد تأیید")

    national_id = models.CharField(max_length=10, null=True, blank=True,
                                    validators=[RegexValidator(regex=r'^\d{10}$', message='کد ملی باید دقیقاً 10 رقم باشد')
                                                                                     ,validate_national_id],verbose_name="کد ملی")
    economic_code = models.CharField(max_length=12, null=True, blank=True, verbose_name="کد اقتصادی")
    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email


class Address(models.Model): 

    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE , verbose_name=" مشتری")
    title_address= models.CharField(max_length=50)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    full_address = models.TextField()
    postcode =models.CharField(max_length=10,validators=[MinLengthValidator(10)])

    def __str__(self):
        return f"{self.city}, {self.province} - {self.full_address}"



class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'اطلاعات'),
        ('success', 'موفقیت'),
        ('warning', 'هشدار'),
        ('danger', 'خطر'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications', verbose_name="کاربر")
    title = models.CharField(max_length=255, verbose_name="عنوان")
    message = models.TextField(verbose_name="متن پیام")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info', verbose_name="نوع اعلان")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    related_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="لینک مرتبط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "اعلان"
        verbose_name_plural = "اعلان‌ها"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
        
    def mark_as_read(self):
        self.is_read = True
        self.save()


class Profile(models.Model):
    
    client  = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')

    legal_info = models.TextField(null=True, blank=True, verbose_name="اطلاعات حقوقی")

    refund_method = models.CharField(max_length=100, null=True, blank=True, verbose_name="روش بازگرداندن پول")
    # Signal برای ایجاد خودکار Profile هنگام ایجاد User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"
    
    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"


class Provider(models.Model):
    provider = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='provider', verbose_name="تامین کننده ")
    company_name = models.CharField(max_length=100, verbose_name="نام شرکت" , blank=True , null=True)
    company_registration_number = models.CharField(max_length=20, verbose_name="شماره ثبت شرکت" , blank=True , null=True)
    company_description = models.TextField(verbose_name="توضیحات شرکت", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "ارائه دهنده"
        verbose_name_plural = "ارائه دهندگان"

    def __str__(self):
        return f"{self.company_name} - {self.user.username}"

    def save(self, *args, **kwargs):
        # Make sure the user is staff when saving a provider
        if not self.user.is_staff:
            self.user.is_staff = True
            self.user.save()
        super().save(*args, **kwargs)



class Fav_Product_List(models.Model):

    client = models.ForeignKey(CustomUser, verbose_name=" مشتری", on_delete=models.CASCADE)
    products=models.ManyToManyField(Product, verbose_name=("محصولات مورد علاقه"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Favorites"




class Offer_Code(models.Model):
    title = models.CharField( max_length=50)

    code = models.CharField(verbose_name="کد تخفیف" , max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(CustomUser, verbose_name="کاربر ") 

    def __str__(self):
        return f" title: {self.title}  \n offer-code : {self.code}  "