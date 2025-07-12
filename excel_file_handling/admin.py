from django.contrib import admin
from .models import ExcelFile, ExcelImportLog

@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'status', 'uploaded_at', 'total_rows', 'processed_rows', 'error_rows']
    list_filter = ['file_type', 'status', 'uploaded_at']
    search_fields = ['title']
    readonly_fields = ['uploaded_at', 'processed_at', 'total_rows', 'processed_rows', 'error_rows']
    
    fieldsets = (
        ('اطلاعات فایل', {
            'fields': ('title', 'file', 'file_type')
        }),
        ('وضعیت پردازش', {
            'fields': ('status', 'uploaded_at', 'processed_at')
        }),
        ('آمار پردازش', {
            'fields': ('total_rows', 'processed_rows', 'error_rows')
        }),
    )

@admin.register(ExcelImportLog)
class ExcelImportLogAdmin(admin.ModelAdmin):
    list_display = ['excel_file', 'level', 'row_number', 'message', 'created_at']
    list_filter = ['level', 'created_at', 'excel_file__file_type']
    search_fields = ['message', 'excel_file__title']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False  # لاگ‌ها فقط باید از طریق کد ایجاد شوند
