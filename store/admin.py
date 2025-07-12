from django.contrib import admin
from django.utils.html import format_html
from .models import *
from mptt.admin import DraggableMPTTAdmin

class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1
    autocomplete_fields = ['color', 'warranty']
    show_change_link = True

class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 1
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return '-'
    image_preview.short_description = 'پیش‌نمایش'

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    autocomplete_fields = ['specification']
    readonly_fields = ['get_unit']
    
    def get_unit(self, obj):
        if obj.specification:
            return obj.specification.unit or '-'
        return '-'
    get_unit.short_description = 'واحد'

class SpecificationInline(admin.TabularInline):
    model = Specification.categories.through
    extra = 1
    verbose_name = "دسته‌بندی"
    verbose_name_plural = "دسته‌بندی‌ها"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_categories', 'brand', 'get_specifications_count', 'is_active']
    search_fields = ['title', 'description', 'brand__name']
    list_filter = ['categories', 'brand', 'is_active']
    filter_horizontal = ['categories', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductSpecificationInline, ProductOptionInline]
    list_editable = ['is_active']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.upload_excel)
        ]
        return custom_urls + urls

    def upload_excel(self, request):
        if request.method == 'POST':
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():
                title = row['title']
                description = row.get('description', '')
                is_active = row.get('is_active', True)
                brand_name = row.get('brand')

                # برند
                brand = None
                if pd.notna(brand_name):
                    brand, _ = Brand.objects.get_or_create(name=brand_name)

                # ساخت محصول
                product = Product.objects.create(
                    title=title,
                    description=description,
                    brand=brand,
                    is_active=bool(is_active),
                )

                # دسته‌بندی‌ها
                category_names = str(row.get('categories', '')).split(',')
                for name in category_names:
                    name = name.strip()
                    if name:
                        category, _ = Category.objects.get_or_create(name=name)
                        product.categories.add(category)

                # تگ‌ها
                tag_names = str(row.get('tags', '')).split(',')
                for name in tag_names:
                    name = name.strip()
                    if name:
                        tag, _ = Tag.objects.get_or_create(name=name)
                        product.tags.add(tag)

            self.message_user(request, "📥 محصولات با موفقیت از فایل اکسل وارد شدند.")
            return redirect("..")
        
        return render(request, 'admin/upload_excel.html')

    def get_categories(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])
    get_categories.short_description = 'دسته‌بندی‌ها'

    def get_specifications_count(self, obj):
        return obj.spec_values.count()
    get_specifications_count.short_description = 'تعداد مشخصات'

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title', 'parent', 'description', 'get_specifications_count')
    list_display_links = ('indented_title',)
    search_fields = ['name', 'description']
    list_filter = ['parent']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['brand']
    inlines = [SpecificationInline]

    def get_specifications_count(self, obj):
        return obj.spec_definitions.count()
    get_specifications_count.short_description = 'تعداد مشخصات'

@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'option_price', 'is_active_discount', 'discount', 'quantity', 'is_active']
    search_fields = ['product__title', 'color__name']
    list_filter = ['is_active', 'is_active_discount', 'color', 'warranty']
    autocomplete_fields = ['product', 'color', 'warranty']
    inlines = [GalleryInline]
    list_editable = ['is_active_discount', 'discount', 'quantity', 'is_active']

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['product_title', 'image_preview', 'alt_text']
    search_fields = ['product__product__title', 'alt_text']
    list_filter = ['product__product']
    readonly_fields = ['image_preview']

    def product_title(self, obj):
        return obj.product.product.title
    product_title.short_description = 'محصول'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return '-'
    image_preview.short_description = 'پیش‌نمایش'

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_preview', 'hex_code']
    search_fields = ['name', 'hex_code']

    def color_preview(self, obj):
        return format_html(
            '<div style="background-color: {}; width: 30px; height: 30px; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.hex_code
        )
    color_preview.short_description = 'رنگ'

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'logo_preview']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['logo_preview']

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.logo.url)
        return '-'
    logo_preview.short_description = 'لوگو'

@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_categories', 'group', 'data_type', 'unit', 'get_usage_count']
    list_filter = ['categories', 'group', 'data_type']
    search_fields = ['name', 'categories__name']
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['categories', 'group']
    filter_horizontal = ['categories']

    def get_categories(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])
    get_categories.short_description = 'دسته‌بندی‌ها'

    def get_usage_count(self, obj):
        return obj.values.count()
    get_usage_count.short_description = 'تعداد استفاده'

@admin.register(SpecificationGroup)
class SpecificationGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_specifications_count']
    search_fields = ['name']
    
    def get_specifications_count(self, obj):
        return obj.specifications.count()
    get_specifications_count.short_description = 'تعداد مشخصات'

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ['product', 'specification', 'get_value', 'get_unit', 'get_data_type', 'is_main']
    list_filter = ['specification__categories', 'specification__data_type', 'is_main']
    search_fields = ['product__title', 'specification__name']
    autocomplete_fields = ['product', 'specification']
    list_select_related = ['product', 'specification']

    def get_value(self, obj):
        value = obj.value()
        if obj.specification.data_type == 'bool':
            return '✓' if value else '✗'
        return value
    get_value.short_description = 'مقدار'

    def get_unit(self, obj):
        return obj.specification.unit if obj.specification.unit else '-'
    get_unit.short_description = 'واحد'

    def get_data_type(self, obj):
        return obj.specification.get_data_type_display()
    get_data_type.short_description = 'نوع داده'

@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'duration', 'is_active')
    list_filter = ('is_active', 'company')
    search_fields = ('name', 'company')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

from django.urls import path
from django.shortcuts import render, redirect
import pandas as pd
from django.utils.text import slugify
