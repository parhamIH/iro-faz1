from django.contrib import admin
from .models import CustomUser, Provider ,Profile ,Address ,Notification ,FavProductList ,OfferCode

#Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):

    
    list_display = ['full_name', 'phone_number', 'email', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['full_name', 'phone_number', 'email']
    list_editable = ['is_active', 'is_staff']
    list_per_page = 20
    
    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.full_name
    
    
@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['provider', 'company_name', 'company_registration_number', 'is_active','created_at','updated_at']
    list_filter = ['is_active']
    search_fields = ['provider__full_name', 'company_name', 'company_registration_number']
    list_editable = ['is_active']
    list_per_page = 20

    class Meta:
        verbose_name = "ارائه دهنده"
        verbose_name_plural = "ارائه دهندگان"

    def __str__(self):
        return self.provider.full_name
    
    

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['client', 'client__phone_number', 'client__email', 'client__is_active', 'client__is_staff']
    list_filter = ['client__is_active', 'client__is_staff']
    search_fields = ['client__full_name', 'client__phone_number', 'client__email']
    list_per_page = 20


@admin.register(OfferCode)
class OfferCodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'created_at','used']
    list_filter = ['created_at']
    search_fields = ['title', 'code']
    list_per_page = 20

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف" 