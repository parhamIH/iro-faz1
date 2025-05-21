from django.db import models

class Address(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=100, verbose_name='عنوان آدرس')  # مثلا: خانه، محل کار
    receiver_name = models.CharField(max_length=100, verbose_name='نام گیرنده')
    receiver_phone = models.CharField(max_length=20, verbose_name='تلفن گیرنده')
    state = models.CharField(max_length=100, verbose_name='استان')
    city = models.CharField(max_length=100, verbose_name='شهر')
    postal_code = models.CharField(max_length=10, verbose_name='کد پستی')
    full_address = models.TextField(verbose_name='آدرس کامل')
    is_default = models.BooleanField(default=False, verbose_name='آدرس پیش‌فرض')
    
    class Meta:
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس‌ها'
        ordering = ['-is_default', 'id']

    def __str__(self):
        return f"{self.title} - {self.receiver_name}"

    def save(self, *args, **kwargs):
        # اگر این آدرس به عنوان پیش‌فرض تنظیم شده، آدرس‌های پیش‌فرض دیگر کاربر را غیرفعال کن
        if self.is_default:
            Address.objects.filter(user=self.user).exclude(id=self.id).update(is_default=False)
        # اگر این اولین آدرس کاربر است، آن را به عنوان پیش‌فرض تنظیم کن
        elif not self.id and not Address.objects.filter(user=self.user).exists():
            self.is_default = True
        super().save(*args, **kwargs)

# مدل سفارشی کاربر
class CustomUser(models.Model):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    phone = models.CharField(max_length=20)
    birth_date = models.DateField()
    is_client = models.BooleanField(default=False)   
    is_provider = models.BooleanField(default=False) 
    is_admin = models.BooleanField(default=False) 

    def __str__(self):
        return self.username

class ClientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='client_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    national_code = models.CharField(max_length=10, blank=True, null=True)
    is_client = models.BooleanField(default=True)    

    def __str__(self):
        return f"Client: {self.user.username} \n code meli: {self.national_code}"

    def get_default_address(self):
        """گرفتن آدرس پیش‌فرض کاربر"""
        return self.addresses.filter(is_default=True).first()

class ProviderProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='provider_profile')
    phone = models.CharField(max_length=20)
    birth_date = models.DateField(blank=True, null=True)
    national_code = models.CharField(max_length=10, blank=True, null=True)
    is_provider = models.BooleanField(default=True)

    def __str__(self):
        return f"Provider: {self.user.username} \n code meli: {self.national_code}"
    