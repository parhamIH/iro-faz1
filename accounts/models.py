# from django.contrib.auth.models import AbstractUser
# from django.db import models

# # مدل سفارشی کاربر
# class CustomUser(AbstractUser):
#     groups = models.ManyToManyField(
#         'auth.Group',
#         verbose_name='groups',
#         blank=True,
#         related_name='custom_user_set',
#         related_query_name='custom_user'
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         verbose_name='user permissions',
#         blank=True,
#         related_name='custom_user_set',
#         related_query_name='custom_user'
#     )
#     phone = models.CharField(max_length=20)
#     address = models.CharField(max_length=255)
#     birth_date = models.DateField()
#     is_client = models.BooleanField(default=False)   
#     is_provider = models.BooleanField(default=False) 
#     is_admin = models.BooleanField(default=False) 

#     def __str__(self):
#         return self.username
    
# # پروفایل کلاینت


# '''
# realtions => cart , order ,notifications ,
# ,,,,, optional -> kife pool 
#  informations (phone , name , address , National code  , bith day )  

# '''
# class ClientProfile(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='client_profile')
#     phone = models.CharField(max_length=20, blank=True, null=True)
#     address = models.CharField(max_length=255, blank=True, null=True)
#     birth_date = models.DateField( blank=True , null=True)
    
#     national_code = models.CharField(max_length=10, blank=True, null=True)#unique=True
   
#     #permission 
#     is_client = models.BooleanField(default=True)    

#     #relations => cart , order ,notifications ,
#     def __str__(self):
#         return f"Client: {self.user.username} \n code meli: {self.national_code}"


# # پروفایل تأمین‌کننده (Provider)
# '''
# realtions => product (read only ) , product-optin(CRUD) + (sell's out put)  
# ,  ???? information (phone , name , address ,owner  National code   , bith day  , )
#  ???? ,notifications  ,  
#      ,,,,,, optional -> kife pool
# '''
# class ProviderProfile(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='provider_profile')
#     phone = models.CharField(max_length=20)
#     address = models.CharField(max_length=255)
    
#     birth_date = models.DateField( blank=True , null=True)
    
#     national_code = models.CharField(max_length=10, blank=True, null=True)#unique=True
   
#     #permission 
#     is_provider = models.BooleanField(default=True)

#     #relations => product (read only ) , product-optin(CRUD) + (sell's out put) - > options (PDF , exel , world) 



#     def __str__(self):
#         return f"Provider: {self.user.username} \n code meli: {self.national_code}"
    