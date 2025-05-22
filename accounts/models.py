from django.db import models

# Create your models here.

from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="کاربر")
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="شماره تلفن")
    is_phone_verified = models.BooleanField(default=False, verbose_name="تأیید شماره تلفن")
    verification_code = models.CharField(max_length=6, null=True, blank=True, verbose_name="کد تأیید")
    verification_code_created_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان ایجاد کد تأیید")
    national_id = models.CharField(max_length=10, null=True, blank=True, verbose_name="کد ملی")
    birth_date = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")
    job = models.CharField(max_length=100, null=True, blank=True, verbose_name="شغل")
    economic_code = models.CharField(max_length=12, null=True, blank=True, verbose_name="کد اقتصادی")
    legal_info = models.TextField(null=True, blank=True, verbose_name="اطلاعات حقوقی")
    refund_method = models.CharField(max_length=100, null=True, blank=True, verbose_name="روش بازگرداندن پول")
    
    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"
    
    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"

# Signal برای ایجاد خودکار Profile هنگام ایجاد User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider')
    company_name = models.CharField(max_length=100, verbose_name="نام شرکت")
    company_registration_number = models.CharField(max_length=20, verbose_name="شماره ثبت شرکت")
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

