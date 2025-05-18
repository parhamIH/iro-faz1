from django.contrib.auth.models import AbstractUser
from django.db import models

# مدل سفارشی کاربر
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    birth_date = models.DateField()
    is_client = models.BooleanField(default=False) # we can use basic user field -> is admin 0 , is staf 0  
    is_provider = models.BooleanField(default=False) # we can use basic user field ->  is admin 0 , is staf 1
    is_admin = models.BooleanField(default=False) # we can use basic user field ->  is admin 1 , is staf 1

    def __str__(self):
        return self.username
    
# پروفایل کلاینت


'''
realtions => cart , order ,notifications ,
,,,,, optional -> kife pool 
 informations (phone , name , address , National code  , bith day )  

'''
class ClientProfile(models.Model):

    def __str__(self):
        return f"Client: {self.user.username}"


# پروفایل تأمین‌کننده (Provider)
'''
realtions => product (read only ) , product-optin(CRUD) + (sell's out put)  
,  ???? information (phone , name , address ,owner  National code   , bith day  , )
 ???? ,notifications  ,  
     ,,,,,, optional -> kife pool
'''
class ProviderProfile(models.Model):
    
    def __str__(self):
        return f"Provider: {self.user.username}"
    