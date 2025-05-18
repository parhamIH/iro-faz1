from django.contrib.auth.models import User
from django.db import models


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ...
    # فیلدهای اختصاصی کلاینت

class ProviderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # فیلدهای اختصاصی تامین‌کننده محصول
    ...

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ... 
