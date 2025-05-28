from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator , MinLengthValidator 
from django.contrib.auth import get_user_model 
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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
    phone_number = models.CharField(max_length=13,validators=[iran_phone_regex],unique=True,blank=True,null=True,)
    date_of_birth = models.DateField(blank=True, null=True)
    
    national_id = models.CharField(max_length=10, null=True, blank=True, validators=[
            RegexValidator(
                regex=r'^\d{10}$', 
                message='کد ملی باید دقیقاً 10 رقم باشد'),
                validate_national_id],verbose_name="کد ملی"
                )
    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email


class Address(models.Model): 

    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title_address= models.CharField(max_length=50)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    full_address = models.TextField()
    postcode =models.CharField(max_length=10,validators=[MinLengthValidator(10)])

    def __str__(self):
        return f"{self.city}, {self.province} - {self.full_address}"
