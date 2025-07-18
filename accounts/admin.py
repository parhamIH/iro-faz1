from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Provider ,Profile ,Address ,Notification ,FavProductList ,OfferCode, DeviceToken

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
    list_display = ['user', 'get_phone_number', 'get_email', 'get_is_active', 'get_is_staff']
    list_filter = ['user__is_active', 'user__is_staff']
    search_fields = ['user__full_name', 'user__phone_number', 'user__email']
    list_per_page = 20

    def get_phone_number(self, obj):
        return obj.user.phone_number
    get_phone_number.short_description = 'شماره تلفن'
    get_phone_number.admin_order_field = 'user__phone_number'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'ایمیل'
    get_email.admin_order_field = 'user__email'

    def get_is_active(self, obj):
        return obj.user.is_active
    get_is_active.short_description = 'فعال'
    get_is_active.boolean = True
    get_is_active.admin_order_field = 'user__is_active'

    def get_is_staff(self, obj):
        return obj.user.is_staff
    get_is_staff.short_description = 'کارمند'
    get_is_staff.boolean = True
    get_is_staff.admin_order_field = 'user__is_staff'

@admin.register(OfferCode)
class OfferCodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'created_at','used']
    list_filter = ['created_at']
    search_fields = ['title', 'code']
    list_per_page = 20

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"

@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_name', 'device_type', 'is_active', 'last_used', 'created_at', 'expires_at']
    list_filter = ['device_type', 'is_active', 'created_at', 'expires_at']
    search_fields = ['user__full_name', 'user__phone_number', 'device_name']
    readonly_fields = ['id', 'token_hash', 'created_at', 'last_used']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        return False  # Device tokens should only be created through the API
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True 