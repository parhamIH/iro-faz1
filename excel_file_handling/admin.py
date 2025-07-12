from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ExcelFile, ExcelImportLog
from .services import ExcelImportService
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'file_type_display', 'status_display', 
        'uploaded_at', 'total_rows', 'processed_rows', 'error_rows',
        'file_size_display', 'actions_display'
    ]
    list_filter = ['file_type', 'status', 'uploaded_at']
    search_fields = ['title', 'file__name']
    readonly_fields = [
        'uploaded_at', 'processed_at', 'total_rows', 
        'processed_rows', 'error_rows', 'file_size_display'
    ]
    actions = ['process_selected_files', 'delete_selected_files']
    
    fieldsets = (
        ('اطلاعات فایل', {
            'fields': ('title', 'file', 'file_type')
        }),
        ('وضعیت پردازش', {
            'fields': ('status', 'uploaded_at', 'processed_at')
        }),
        ('آمار پردازش', {
            'fields': ('total_rows', 'processed_rows', 'error_rows', 'file_size_display')
        }),
    )
    
    def file_type_display(self, obj):
        return obj.get_file_type_display()
    file_type_display.short_description = 'نوع فایل'
    
    def status_display(self, obj):
        status_colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'وضعیت'
    
    def file_size_display(self, obj):
        return obj.get_file_size()
    file_size_display.short_description = 'حجم فایل'
    
    def actions_display(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}">پردازش</a>',
                reverse('admin:process_excel_file', args=[obj.id])
            )
        elif obj.status == 'completed':
            return format_html(
                '<a class="button" href="{}">مشاهده لاگ‌ها</a>',
                reverse('admin:excel_file_handling_excelimportlog_changelist') + f'?excel_file__id__exact={obj.id}'
            )
        return '-'
    actions_display.short_description = 'عملیات'
    
    def process_selected_files(self, request, queryset):
        """پردازش فایل‌های انتخاب شده"""
        processed = 0
        for excel_file in queryset.filter(status='pending'):
            try:
                service = ExcelImportService(excel_file.id)
                service.process_file()
                processed += 1
            except Exception as e:
                messages.error(request, f'خطا در پردازش فایل {excel_file.title}: {str(e)}')
        
        if processed > 0:
            messages.success(request, f'{processed} فایل با موفقیت پردازش شد')
        
        return HttpResponseRedirect(request.get_full_path())
    process_selected_files.short_description = 'پردازش فایل‌های انتخاب شده'
    
    def delete_selected_files(self, request, queryset):
        """حذف فایل‌های انتخاب شده"""
        count = queryset.count()
        queryset.delete()
        messages.success(request, f'{count} فایل حذف شد')
        return HttpResponseRedirect(request.get_full_path())
    delete_selected_files.short_description = 'حذف فایل‌های انتخاب شده'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:file_id>/process/',
                self.admin_site.admin_view(self.process_file_view),
                name='process_excel_file',
            ),
        ]
        return custom_urls + urls
    
    def process_file_view(self, request, file_id):
        """نمایش صفحه پردازش فایل"""
        try:
            excel_file = ExcelFile.objects.get(id=file_id)
            if excel_file.status == 'pending':
                service = ExcelImportService(excel_file.id)
                service.process_file()
                messages.success(request, f'فایل {excel_file.title} با موفقیت پردازش شد')
            else:
                messages.warning(request, f'فایل {excel_file.title} در وضعیت {excel_file.get_status_display()} است')
        except ExcelFile.DoesNotExist:
            messages.error(request, 'فایل یافت نشد')
        except Exception as e:
            messages.error(request, f'خطا در پردازش فایل: {str(e)}')
        
        return redirect('admin:excel_file_handling_excelfile_changelist')

@admin.register(ExcelImportLog)
class ExcelImportLogAdmin(admin.ModelAdmin):
    list_display = [
        'excel_file', 'level_display', 'row_number', 
        'message_short', 'created_at'
    ]
    list_filter = ['level', 'created_at', 'excel_file__file_type']
    search_fields = ['message', 'excel_file__title']
    readonly_fields = ['excel_file', 'row_number', 'level', 'message', 'created_at']
    ordering = ['-created_at']
    
    def level_display(self, obj):
        level_colors = {
            'info': 'blue',
            'warning': 'orange',
            'error': 'red',
            'success': 'green'
        }
        color = level_colors.get(obj.level, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_level_display()
        )
    level_display.short_description = 'سطح'
    
    def message_short(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_short.short_description = 'پیام'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    fieldsets = (
        ('اطلاعات فایل', {
            'fields': ('excel_file',)
        }),
        ('جزئیات لاگ', {
            'fields': ('level', 'row_number', 'message', 'created_at')
        }),
    )
