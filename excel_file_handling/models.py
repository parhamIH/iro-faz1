from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import os

class ExcelFile(models.Model):
    """مدل برای ذخیره فایل‌های Excel آپلود شده"""
    
    FILE_TYPE_CHOICES = [
        ('products', 'محصولات'),
        ('categories', 'دسته‌بندی‌ها'),
        ('brands', 'برندها'),
        ('specifications', 'مشخصات'),
        ('specification_groups', 'گروه‌های مشخصات'),
        ('colors', 'رنگ‌ها'),
        ('warranties', 'گارانتی‌ها'),
        ('tags', 'تگ‌ها'),
        ('product_options', 'ویژگی‌های محصول'),
        ('product_specifications', 'مقادیر مشخصات محصول'),
        ('articles', 'مقالات'),
        ('article_categories', 'دسته‌بندی‌های مقاله'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار پردازش'),
        ('processing', 'در حال پردازش'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
    ]
    
    title = models.CharField(max_length=255, verbose_name='عنوان فایل')
    file = models.FileField(
        upload_to='excel_files/',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        verbose_name='فایل Excel'
    )
    file_type = models.CharField(
        max_length=30,
        choices=FILE_TYPE_CHOICES,
        verbose_name='نوع فایل'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پردازش')
    total_rows = models.PositiveIntegerField(default=0, verbose_name='تعداد کل ردیف‌ها')
    processed_rows = models.PositiveIntegerField(default=0, verbose_name='تعداد ردیف‌های پردازش شده')
    error_rows = models.PositiveIntegerField(default=0, verbose_name='تعداد ردیف‌های دارای خطا')
    
    class Meta:
        verbose_name = 'فایل Excel'
        verbose_name_plural = 'فایل‌های Excel'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_file_type_display()}"
    
    def get_file_name(self):
        return os.path.basename(self.file.name)
    
    def get_file_size(self):
        if self.file:
            return f"{self.file.size / 1024:.1f} KB"
        return "0 KB"

class ExcelImportLog(models.Model):
    """مدل برای ثبت لاگ عملیات‌های import"""
    
    LOG_LEVEL_CHOICES = [
        ('info', 'اطلاعات'),
        ('warning', 'هشدار'),
        ('error', 'خطا'),
        ('success', 'موفق'),
    ]
    
    excel_file = models.ForeignKey(
        ExcelFile,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='فایل Excel'
    )
    row_number = models.PositiveIntegerField(null=True, blank=True, verbose_name='شماره ردیف')
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES, verbose_name='سطح')
    message = models.TextField(verbose_name='پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'لاگ import'
        verbose_name_plural = 'لاگ‌های import'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.excel_file.title} - {self.get_level_display()} - {self.message[:50]}"
