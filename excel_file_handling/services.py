import pandas as pd
import openpyxl
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import ExcelFile, ExcelImportLog
from store.models import (
    Product, Category, Brand, Specification, ProductSpecification, 
    Color, Warranty, Tag, SpecificationGroup, ProductOption,
    Article, ArticleCategory
)
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

class ExcelImportService:
    """سرویس برای پردازش فایل‌های Excel و import کردن داده‌ها"""
    
    def __init__(self, excel_file_id):
        self.excel_file = ExcelFile.objects.get(id=excel_file_id)
        self.logs = []
    
    def log_message(self, level, message, row_number=None):
        """ثبت پیام در لاگ"""
        log = ExcelImportLog(
            excel_file=self.excel_file,
            level=level,
            message=message,
            row_number=row_number
        )
        log.save()
        self.logs.append(log)
    
    def update_file_status(self, status, **kwargs):
        """بروزرسانی وضعیت فایل"""
        for key, value in kwargs.items():
            setattr(self.excel_file, key, value)
        self.excel_file.status = status
        self.excel_file.save()
    
    def read_excel_file(self):
        """خواندن فایل Excel"""
        try:
            df = pd.read_excel(self.excel_file.file.path)
            self.update_file_status('processing', total_rows=len(df))
            self.log_message('info', f'فایل Excel با {len(df)} ردیف خوانده شد')
            return df
        except Exception as e:
            self.log_message('error', f'خطا در خواندن فایل Excel: {str(e)}')
            self.update_file_status('failed')
            raise
    
    def import_specification_groups(self, df):
        """Import کردن گروه‌های مشخصات"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    name = str(row.get('name', '')).strip()
                    if not name:
                        self.log_message('warning', f'ردیف {index + 2}: نام گروه مشخصات خالی است', index + 2)
                        errors += 1
                        continue
                    
                    group, created = SpecificationGroup.objects.get_or_create(name=name)
                    
                    if created:
                        self.log_message('success', f'گروه مشخصات "{name}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'گروه مشخصات "{name}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def import_tags(self, df):
        """Import کردن تگ‌ها"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    name = str(row.get('name', '')).strip()
                    if not name:
                        self.log_message('warning', f'ردیف {index + 2}: نام تگ خالی است', index + 2)
                        errors += 1
                        continue
                    
                    tag, created = Tag.objects.get_or_create(name=name)
                    
                    if created:
                        self.log_message('success', f'تگ "{name}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'تگ "{name}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def import_article_categories(self, df):
        """Import کردن دسته‌بندی‌های مقاله"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    name = str(row.get('name', '')).strip()
                    if not name:
                        self.log_message('warning', f'ردیف {index + 2}: نام دسته‌بندی مقاله خالی است', index + 2)
                        errors += 1
                        continue
                    
                    category, created = ArticleCategory.objects.get_or_create(name=name)
                    
                    if created:
                        self.log_message('success', f'دسته‌بندی مقاله "{name}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'دسته‌بندی مقاله "{name}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def import_articles(self, df):
        """Import کردن مقالات"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    title = str(row.get('title', '')).strip()
                    if not title:
                        self.log_message('warning', f'ردیف {index + 2}: عنوان مقاله خالی است', index + 2)
                        errors += 1
                        continue
                    
                    content = str(row.get('content', '')).strip()
                    if not content:
                        self.log_message('warning', f'ردیف {index + 2}: محتوای مقاله خالی است', index + 2)
                        errors += 1
                        continue
                    
                    category_name = str(row.get('category', '')).strip()
                    category = None
                    if category_name:
                        try:
                            category = ArticleCategory.objects.get(name=category_name)
                        except ArticleCategory.DoesNotExist:
                            self.log_message('warning', f'دسته‌بندی مقاله "{category_name}" یافت نشد', index + 2)
                    
                    tags_str = str(row.get('tags', '')).strip()
                    tags = []
                    if tags_str:
                        tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                        tags = Tag.objects.filter(name__in=tag_names)
                    
                    is_published = bool(row.get('is_published', True))
                    
                    article, created = Article.objects.get_or_create(
                        title=title,
                        defaults={
                            'content': content,
                            'category': category,
                            'is_published': is_published
                        }
                    )
                    
                    if tags:
                        article.tags.set(tags)
                    
                    if created:
                        self.log_message('success', f'مقاله "{title}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'مقاله "{title}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def import_brands(self, df):
        """Import کردن برندها"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    name = str(row.get('name', '')).strip()
                    if not name:
                        self.log_message('warning', f'ردیف {index + 2}: نام برند خالی است', index + 2)
                        errors += 1
                        continue
                    
                    description = str(row.get('description', '')).strip()
                    
                    brand, created = Brand.objects.get_or_create(
                        name=name,
                        defaults={'description': description}
                    )
                    
                    if created:
                        self.log_message('success', f'برند "{name}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'برند "{name}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def import_categories(self, df):
        """Import کردن دسته‌بندی‌ها"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    name = str(row.get('name', '')).strip()
                    if not name:
                        self.log_message('warning', f'ردیف {index + 2}: نام دسته‌بندی خالی است', index + 2)
                        errors += 1
                        continue
                    
                    description = str(row.get('description', '')).strip()
                    parent_name = str(row.get('parent', '')).strip()
                    
                    # ایجاد یا پیدا کردن parent
                    parent = None
                    if parent_name:
                        try:
                            parent = Category.objects.get(name=parent_name)
                        except Category.DoesNotExist:
                            self.log_message('warning', f'دسته‌بندی والد "{parent_name}" یافت نشد', index + 2)
                    
                    category, created = Category.objects.get_or_create(
                        name=name,
                        defaults={
                            'description': description,
                            'parent': parent
                        }
                    )
                    
                    if created:
                        self.log_message('success', f'دسته‌بندی "{name}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'دسته‌بندی "{name}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def import_colors(self, df):
        """Import کردن رنگ‌ها"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    name = str(row.get('name', '')).strip()
                    if not name:
                        self.log_message('warning', f'ردیف {index + 2}: نام رنگ خالی است', index + 2)
                        errors += 1
                        continue
                    
                    hex_code = str(row.get('hex_code', '')).strip()
                    if not hex_code.startswith('#'):
                        hex_code = f'#{hex_code}'
                    
                    color, created = Color.objects.get_or_create(
                        name=name,
                        defaults={'hex_code': hex_code}
                    )
                    
                    if created:
                        self.log_message('success', f'رنگ "{name}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'رنگ "{name}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def import_warranties(self, df):
        """Import کردن گارانتی‌ها"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    name = str(row.get('name', '')).strip()
                    if not name:
                        self.log_message('warning', f'ردیف {index + 2}: نام گارانتی خالی است', index + 2)
                        errors += 1
                        continue
                    
                    company = str(row.get('company', '')).strip()
                    duration = row.get('duration', 0)
                    description = str(row.get('description', '')).strip()
                    terms_conditions = str(row.get('terms_conditions', '')).strip()
                    support_phone = str(row.get('support_phone', '')).strip()
                    registration_required = bool(row.get('registration_required', False))
                    
                    warranty, created = Warranty.objects.get_or_create(
                        name=name,
                        defaults={
                            'company': company,
                            'duration': duration,
                            'description': description,
                            'terms_conditions': terms_conditions,
                            'support_phone': support_phone,
                            'registration_required': registration_required
                        }
                    )
                    
                    if created:
                        self.log_message('success', f'گارانتی "{name}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'گارانتی "{name}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def import_specifications(self, df):
        """Import کردن مشخصات فنی"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    name = str(row.get('name', '')).strip()
                    if not name:
                        self.log_message('warning', f'ردیف {index + 2}: نام مشخصه خالی است', index + 2)
                        errors += 1
                        continue
                    
                    data_type = str(row.get('data_type', '')).strip()
                    if data_type not in ['int', 'decimal', 'str', 'bool']:
                        self.log_message('warning', f'ردیف {index + 2}: نوع داده نامعتبر است', index + 2)
                        errors += 1
                        continue
                    
                    unit = str(row.get('unit', '')).strip()
                    is_main = bool(row.get('is_main', False))
                    
                    # پیدا کردن گروه مشخصات
                    group_name = str(row.get('group', '')).strip()
                    group = None
                    if group_name:
                        try:
                            group = SpecificationGroup.objects.get(name=group_name)
                        except SpecificationGroup.DoesNotExist:
                            self.log_message('warning', f'گروه مشخصات "{group_name}" یافت نشد', index + 2)
                    
                    # پیدا کردن دسته‌بندی‌ها
                    categories_str = str(row.get('categories', '')).strip()
                    categories = []
                    if categories_str:
                        category_names = [cat.strip() for cat in categories_str.split(',') if cat.strip()]
                        categories = Category.objects.filter(name__in=category_names)
                    
                    spec, created = Specification.objects.get_or_create(
                        name=name,
                        defaults={
                            'data_type': data_type,
                            'unit': unit,
                            'is_main': is_main,
                            'group': group
                        }
                    )
                    
                    if categories:
                        spec.categories.set(categories)
                    
                    if created:
                        self.log_message('success', f'مشخصه "{name}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'مشخصه "{name}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def import_products(self, df):
        """Import کردن محصولات"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    title = str(row.get('title', '')).strip()
                    if not title:
                        self.log_message('warning', f'ردیف {index + 2}: عنوان محصول خالی است', index + 2)
                        errors += 1
                        continue
                    
                    description = str(row.get('description', '')).strip()
                    brand_name = str(row.get('brand', '')).strip()
                    
                    # پیدا کردن برند
                    brand = None
                    if brand_name:
                        try:
                            brand = Brand.objects.get(name=brand_name)
                        except Brand.DoesNotExist:
                            self.log_message('warning', f'برند "{brand_name}" یافت نشد', index + 2)
                    
                    # پیدا کردن دسته‌بندی‌ها
                    categories_str = str(row.get('categories', '')).strip()
                    categories = []
                    if categories_str:
                        category_names = [cat.strip() for cat in categories_str.split(',') if cat.strip()]
                        categories = Category.objects.filter(name__in=category_names)
                    
                    # پیدا کردن تگ‌ها
                    tags_str = str(row.get('tags', '')).strip()
                    tags = []
                    if tags_str:
                        tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                        tags = Tag.objects.filter(name__in=tag_names)
                    
                    is_active = bool(row.get('is_active', True))
                    
                    product, created = Product.objects.get_or_create(
                        title=title,
                        defaults={
                            'description': description,
                            'brand': brand,
                            'is_active': is_active
                        }
                    )
                    
                    if categories:
                        product.categories.set(categories)
                    if tags:
                        product.tags.set(tags)
                    
                    if created:
                        self.log_message('success', f'محصول "{title}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'محصول "{title}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def import_product_options(self, df):
        """Import کردن ویژگی‌های محصول"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    product_title = str(row.get('product', '')).strip()
                    if not product_title:
                        self.log_message('warning', f'ردیف {index + 2}: نام محصول خالی است', index + 2)
                        errors += 1
                        continue
                    
                    # پیدا کردن محصول
                    try:
                        product = Product.objects.get(title=product_title)
                    except Product.DoesNotExist:
                        self.log_message('warning', f'محصول "{product_title}" یافت نشد', index + 2)
                        errors += 1
                        continue
                    
                    # پیدا کردن رنگ
                    color_name = str(row.get('color', '')).strip()
                    color = None
                    if color_name:
                        try:
                            color = Color.objects.get(name=color_name)
                        except Color.DoesNotExist:
                            self.log_message('warning', f'رنگ "{color_name}" یافت نشد', index + 2)
                    
                    # پیدا کردن گارانتی
                    warranty_name = str(row.get('warranty', '')).strip()
                    warranty = None
                    if warranty_name:
                        try:
                            warranty = Warranty.objects.get(name=warranty_name)
                        except Warranty.DoesNotExist:
                            self.log_message('warning', f'گارانتی "{warranty_name}" یافت نشد', index + 2)
                    
                    option_price = row.get('option_price', 0)
                    quantity = row.get('quantity', 1)
                    is_active = bool(row.get('is_active', True))
                    is_active_discount = bool(row.get('is_active_discount', False))
                    discount = row.get('discount', 0)
                    
                    product_option, created = ProductOption.objects.get_or_create(
                        product=product,
                        color=color,
                        defaults={
                            'option_price': option_price,
                            'quantity': quantity,
                            'is_active': is_active,
                            'warranty': warranty,
                            'is_active_discount': is_active_discount,
                            'discount': discount
                        }
                    )
                    
                    if created:
                        self.log_message('success', f'ویژگی محصول برای "{product_title}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'ویژگی محصول برای "{product_title}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def import_product_specifications(self, df):
        """Import کردن مقادیر مشخصات محصول"""
        processed = 0
        errors = 0
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    product_title = str(row.get('product', '')).strip()
                    if not product_title:
                        self.log_message('warning', f'ردیف {index + 2}: نام محصول خالی است', index + 2)
                        errors += 1
                        continue
                    
                    spec_name = str(row.get('specification', '')).strip()
                    if not spec_name:
                        self.log_message('warning', f'ردیف {index + 2}: نام مشخصه خالی است', index + 2)
                        errors += 1
                        continue
                    
                    # پیدا کردن محصول
                    try:
                        product = Product.objects.get(title=product_title)
                    except Product.DoesNotExist:
                        self.log_message('warning', f'محصول "{product_title}" یافت نشد', index + 2)
                        errors += 1
                        continue
                    
                    # پیدا کردن مشخصه
                    try:
                        specification = Specification.objects.get(name=spec_name)
                    except Specification.DoesNotExist:
                        self.log_message('warning', f'مشخصه "{spec_name}" یافت نشد', index + 2)
                        errors += 1
                        continue
                    
                    # مقدار مشخصه بر اساس نوع داده
                    int_value = row.get('int_value', None)
                    decimal_value = row.get('decimal_value', None)
                    str_value = str(row.get('str_value', '')).strip() if row.get('str_value') else None
                    bool_value = row.get('bool_value', None)
                    is_main = bool(row.get('is_main', False))
                    
                    product_spec, created = ProductSpecification.objects.get_or_create(
                        product=product,
                        specification=specification,
                        defaults={
                            'int_value': int_value,
                            'decimal_value': decimal_value,
                            'str_value': str_value,
                            'bool_value': bool_value,
                            'is_main': is_main
                        }
                    )
                    
                    if created:
                        self.log_message('success', f'مقدار مشخصه برای "{product_title}" - "{spec_name}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'مقدار مشخصه برای "{product_title}" - "{spec_name}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def process_file(self):
        """پردازش فایل Excel بر اساس نوع آن"""
        try:
            df = self.read_excel_file()
            
            if self.excel_file.file_type == 'brands':
                processed, errors = self.import_brands(df)
            elif self.excel_file.file_type == 'categories':
                processed, errors = self.import_categories(df)
            elif self.excel_file.file_type == 'colors':
                processed, errors = self.import_colors(df)
            elif self.excel_file.file_type == 'warranties':
                processed, errors = self.import_warranties(df)
            elif self.excel_file.file_type == 'specifications':
                processed, errors = self.import_specifications(df)
            elif self.excel_file.file_type == 'specification_groups':
                processed, errors = self.import_specification_groups(df)
            elif self.excel_file.file_type == 'tags':
                processed, errors = self.import_tags(df)
            elif self.excel_file.file_type == 'products':
                processed, errors = self.import_products(df)
            elif self.excel_file.file_type == 'product_options':
                processed, errors = self.import_product_options(df)
            elif self.excel_file.file_type == 'product_specifications':
                processed, errors = self.import_product_specifications(df)
            elif self.excel_file.file_type == 'articles':
                processed, errors = self.import_articles(df)
            elif self.excel_file.file_type == 'article_categories':
                processed, errors = self.import_article_categories(df)
            else:
                raise ValueError(f'نوع فایل "{self.excel_file.file_type}" پشتیبانی نمی‌شود')
            
            self.update_file_status(
                'completed',
                processed_rows=processed,
                error_rows=errors,
                processed_at=timezone.now()
            )
            
            self.log_message('success', f'پردازش فایل تکمیل شد. {processed} ردیف پردازش شد و {errors} خطا رخ داد')
            
        except Exception as e:
            self.log_message('error', f'خطا در پردازش فایل: {str(e)}')
            self.update_file_status('failed')
            raise 