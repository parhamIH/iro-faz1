from django.contrib import admin
from .models import (
    Category, Product, Feature,
    ProductOption, Gallery, Color, Brand
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'description']
    search_fields = ['name', 'description']
    list_filter = ['parent']
    prepopulated_fields = {'slug': ('name',)}

class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1
    autocomplete_fields = ['color']

class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_categories', 'brand']
    search_fields = ['title', 'description', 'brand__name']
    list_filter = ['categories', 'brand', 'is_active']
    filter_horizontal = ['categories', 'feature']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductOptionInline]

    def get_categories(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])
    get_categories.short_description = 'دسته‌بندی‌ها'

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'category', 'is_main_feature']
    list_filter = ['category', 'is_main_feature']
    search_fields = ['name', 'value', 'category__name']
    list_editable = ['is_main_feature']

@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ['product', 'get_feature_info', 'color', 'option_price', 'is_active_discount', 'discount']
    search_fields = ['product__title', 'color__name']
    list_filter = ['is_active', 'is_active_discount', 'color']
    autocomplete_fields = ['product', 'color']
    inlines = [GalleryInline]

    def get_feature_info(self, obj):
        features = obj.product.feature.all()
        return ", ".join([f"{f.name}: {f.value}" for f in features])
    get_feature_info.short_description = 'ویژگی‌ها'

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['product__product', 'image', 'alt_text']
    search_fields = ['product__product__title', 'alt_text']
    list_filter = ['product__product']

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code']
    search_fields = ['name', 'hex_code']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
