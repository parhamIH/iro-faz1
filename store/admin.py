from django.contrib import admin
from .models import (
    Category, Product, Feature, InstallmentPlan,
    ProductFeatureValue, ProductOption, Discount, Gallery, Color, Brand
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
    search_fields = ('name', 'parent__name')
    list_filter = ('parent',)

class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 1

class ProductFeatureValueInline(admin.TabularInline):
    model = ProductFeatureValue
    extra = 1

class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'base_price_cash', 'get_categories_display')
    search_fields = ('title', 'categories__name')
    list_filter = ('categories',)
    filter_horizontal = ('categories', 'installment_plans', 'discounts')
    inlines = [ProductFeatureValueInline, ProductOptionInline]

    def get_categories_display(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories_display.short_description = 'Categories'

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'months', 'prepayment', 'get_interest_rate_display', 'calculate_monthly_installment_display')
    search_fields = ('title', 'product__title')
    list_filter = ('months', 'product__categories')

    def get_interest_rate_display(self, obj):
        return f"{obj.get_interest_rate()}%"
    get_interest_rate_display.short_description = 'Interest Rate'

    def calculate_monthly_installment_display(self, obj):
        return f"{obj.calculate_monthly_installment():,.0f} تومان"
    calculate_monthly_installment_display.short_description = 'Monthly Installment'

@admin.register(ProductFeatureValue)
class ProductFeatureValueAdmin(admin.ModelAdmin):
    list_display = ('product', 'feature', 'value')
    search_fields = ('product__title', 'feature__name', 'value')
    list_filter = ('feature', 'product__categories')

@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ('product', 'feature', 'value', 'color', 'price_change')
    search_fields = ('product__title', 'feature__name', 'value', 'color__name')
    list_filter = ('feature', 'color', 'product__categories')
    inlines = [GalleryInline]

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'start_date', 'end_date', 'is_active')
    search_fields = ('name',)
    list_filter = ('start_date', 'end_date')

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'alt_text')
    search_fields = ('product__product__title', 'alt_text')
    list_filter = ('product__product__categories',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')
    search_fields = ('name', 'hex_code')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
