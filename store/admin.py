from django.contrib import admin
from .models import (
    Category, Product, Feature,
 ProductOption, Discount, Gallery, Color, Brand
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
    search_fields = ('name', 'parent__name')
    list_filter = ('parent',)

class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1
    autocomplete_fields = ['feature', 'color']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'base_price_cash', 'get_categories_display', 'brand')
    search_fields = ('title', 'categories__name', 'brand__name')
    list_filter = ('categories', 'brand')
    filter_horizontal = ('categories', 'discounts')
    inlines = [ ProductOptionInline]
    prepopulated_fields = {'slug': ('title',)}

    def get_categories_display(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories_display.short_description = 'دسته‌بندی‌ها'

@admin.register(Feature)
class FeatureDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'unit', 'is_main_feature', 'category', 'display_order')
    list_filter = ('type', 'is_main_feature', 'category')
    search_fields = ('name', 'category__name')
    ordering = ('category', 'display_order', 'name')
    list_editable = ('display_order', 'is_main_feature')

@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ('product', 'feature', 'feature_value', 'color', 'option_price')
    search_fields = ('product__title', 'feature__name', 'feature_value', 'color__name')
    list_filter = ('feature', 'color', 'product__categories')
    autocomplete_fields = ['product', 'feature', 'color']

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
