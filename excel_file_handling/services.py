import pandas as pd
import openpyxl
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import ExcelFile, ExcelImportLog
from store.models import Product, Category, Brand, Specification, ProductSpecification, Color, Warranty, Tag
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
                    category_names = str(row.get('categories', '')).strip()
                    tag_names = str(row.get('tags', '')).strip()
                    
                    # پیدا کردن برند
                    brand = None
                    if brand_name:
                        try:
                            brand = Brand.objects.get(name=brand_name)
                        except Brand.DoesNotExist:
                            self.log_message('warning', f'برند "{brand_name}" یافت نشد', index + 2)
                    
                    # ایجاد محصول
                    product, created = Product.objects.get_or_create(
                        title=title,
                        defaults={
                            'description': description,
                            'brand': brand
                        }
                    )
                    
                    # اضافه کردن دسته‌بندی‌ها
                    if category_names:
                        category_list = [cat.strip() for cat in category_names.split(',')]
                        for cat_name in category_list:
                            try:
                                category = Category.objects.get(name=cat_name)
                                product.categories.add(category)
                            except Category.DoesNotExist:
                                self.log_message('warning', f'دسته‌بندی "{cat_name}" یافت نشد', index + 2)
                    
                    # اضافه کردن تگ‌ها
                    if tag_names:
                        tag_list = [tag.strip() for tag in tag_names.split(',')]
                        for tag_name in tag_list:
                            tag, _ = Tag.objects.get_or_create(name=tag_name)
                            product.tags.add(tag)
                    
                    if created:
                        self.log_message('success', f'محصول "{title}" ایجاد شد', index + 2)
                    else:
                        self.log_message('info', f'محصول "{title}" قبلاً وجود دارد', index + 2)
                    
                    processed += 1
                    
            except Exception as e:
                self.log_message('error', f'خطا در ردیف {index + 2}: {str(e)}', index + 2)
                errors += 1
        
        return processed, errors
    
    def process_file(self):
        """پردازش کامل فایل Excel"""
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
            elif self.excel_file.file_type == 'products':
                processed, errors = self.import_products(df)
            else:
                raise ValueError(f'نوع فایل {self.excel_file.file_type} پشتیبانی نمی‌شود')
            
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