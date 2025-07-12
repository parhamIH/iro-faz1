from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from .models import ExcelFile, ExcelImportLog
from .services import ExcelImportService
from .forms import ExcelFileUploadForm
import threading
import json

def superuser_required(view_func):
    """دکوراتور برای محدود کردن دسترسی فقط به superuser"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin:login')
        if not request.user.is_superuser:
            raise PermissionDenied("فقط مدیران سیستم می‌توانند به این بخش دسترسی داشته باشند.")
        return view_func(request, *args, **kwargs)
    return wrapper

@superuser_required
def upload_excel(request):
    """صفحه آپلود فایل Excel"""
    if request.method == 'POST':
        form = ExcelFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.save()
            messages.success(request, f'فایل "{excel_file.title}" با موفقیت آپلود شد.')
            return redirect('excel_file_handling:root')
    else:
        form = ExcelFileUploadForm()
    
    context = {
        'form': form,
        'file_types': ExcelFile.FILE_TYPE_CHOICES
    }
    return render(request, 'excel_file_handling/upload.html', context)

@superuser_required
def file_list(request):
    """لیست فایل‌های Excel"""
    files = ExcelFile.objects.all().order_by('-uploaded_at')
    context = {
        'files': files
    }
    return render(request, 'excel_file_handling/file_list.html', context)

@superuser_required
def file_detail(request, file_id):
    """جزئیات فایل Excel و لاگ‌های آن"""
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    logs = excel_file.logs.all().order_by('-created_at')
    
    context = {
        'excel_file': excel_file,
        'logs': logs
    }
    return render(request, 'excel_file_handling/file_detail.html', context)

@superuser_required
def process_file(request, file_id):
    """پردازش فایل Excel"""
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    
    if excel_file.status == 'processing':
        messages.warning(request, 'فایل در حال پردازش است.')
        return redirect('excel_file_handling:file_detail', file_id=file_id)
    
    if excel_file.status == 'completed':
        messages.info(request, 'فایل قبلاً پردازش شده است.')
        return redirect('excel_file_handling:file_detail', file_id=file_id)
    
    try:
        # پردازش در background
        def process_in_background():
            service = ExcelImportService(file_id)
            service.process_file()
        
        thread = threading.Thread(target=process_in_background)
        thread.start()
        
        messages.success(request, f'پردازش فایل "{excel_file.title}" شروع شد.')
        
    except Exception as e:
        messages.error(request, f'خطا در شروع پردازش: {str(e)}')
    
    return redirect('excel_file_handling:file_detail', file_id=file_id)

@superuser_required
def delete_file(request, file_id):
    """حذف فایل Excel"""
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    
    if request.method == 'POST':
        title = excel_file.title
        excel_file.delete()
        messages.success(request, f'فایل "{title}" با موفقیت حذف شد.')
        return redirect('excel_file_handling:root')
    
    context = {
        'excel_file': excel_file
    }
    return render(request, 'excel_file_handling/delete_confirm.html', context)

@superuser_required
@require_http_methods(["POST"])
def process_file_ajax(request, file_id):
    """پردازش فایل Excel با AJAX"""
    try:
        excel_file = get_object_or_404(ExcelFile, id=file_id)
        
        if excel_file.status == 'processing':
            return JsonResponse({
                'status': 'error',
                'message': 'فایل در حال پردازش است.'
            })
        
        if excel_file.status == 'completed':
            return JsonResponse({
                'status': 'info',
                'message': 'فایل قبلاً پردازش شده است.'
            })
        
        # پردازش در background
        def process_in_background():
            service = ExcelImportService(file_id)
            service.process_file()
        
        thread = threading.Thread(target=process_in_background)
        thread.start()
        
        return JsonResponse({
            'status': 'success',
            'message': f'پردازش فایل "{excel_file.title}" شروع شد.'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'خطا در شروع پردازش: {str(e)}'
        })

@superuser_required
def get_file_status(request, file_id):
    """دریافت وضعیت فایل با AJAX"""
    try:
        excel_file = get_object_or_404(ExcelFile, id=file_id)
        
        return JsonResponse({
            'status': excel_file.status,
            'total_rows': excel_file.total_rows,
            'processed_rows': excel_file.processed_rows,
            'error_rows': excel_file.error_rows,
            'uploaded_at': excel_file.uploaded_at.isoformat() if excel_file.uploaded_at else None,
            'processed_at': excel_file.processed_at.isoformat() if excel_file.processed_at else None,
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@superuser_required
def download_template(request, file_type):
    """دانلود قالب Excel"""
    import pandas as pd
    from django.http import HttpResponse
    from io import BytesIO
    
    # تعریف ستون‌های قالب بر اساس نوع فایل
    templates = {
        'brands': {
            'columns': ['name', 'description'],
            'sample_data': [
                ['سامسونگ', 'شرکت سامسونگ الکترونیکس'],
                ['اپل', 'شرکت اپل'],
                ['شیائومی', 'شرکت شیائومی']
            ]
        },
        'categories': {
            'columns': ['name', 'description', 'parent'],
            'sample_data': [
                ['الکترونیک', 'محصولات الکترونیکی', ''],
                ['موبایل', 'گوشی‌های موبایل', 'الکترونیک'],
                ['لپ‌تاپ', 'لپ‌تاپ‌ها', 'الکترونیک']
            ]
        },
        'colors': {
            'columns': ['name', 'hex_code'],
            'sample_data': [
                ['قرمز', '#FF0000'],
                ['آبی', '#0000FF'],
                ['سبز', '#008000']
            ]
        },
        'warranties': {
            'columns': ['name', 'company', 'duration', 'description', 'terms_conditions', 'support_phone', 'registration_required'],
            'sample_data': [
                ['گارانتی 1 ساله', 'شرکت گارانتی', 12, 'گارانتی کامل', 'شرایط گارانتی', '02112345678', True],
                ['گارانتی 2 ساله', 'شرکت گارانتی', 24, 'گارانتی کامل', 'شرایط گارانتی', '02112345678', False]
            ]
        },
        'products': {
            'columns': ['title', 'description', 'brand', 'categories', 'tags'],
            'sample_data': [
                ['گوشی سامسونگ Galaxy S21', 'گوشی هوشمند سامسونگ', 'سامسونگ', 'موبایل', 'گوشی,هوشمند'],
                ['لپ‌تاپ اپل MacBook Pro', 'لپ‌تاپ اپل', 'اپل', 'لپ‌تاپ', 'لپ‌تاپ,اپل']
            ]
        }
    }
    
    if file_type not in templates:
        return JsonResponse({'error': 'نوع فایل نامعتبر است'})
    
    template = templates[file_type]
    
    # ایجاد DataFrame
    df = pd.DataFrame(template['sample_data'], columns=template['columns'])
    
    # ایجاد فایل Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Template', index=False)
    
    output.seek(0)
    
    # ارسال فایل
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{file_type}_template.xlsx"'
    
    return response

def handler403(request, exception=None):
    """Custom 403 error handler"""
    return render(request, 'excel_file_handling/403.html', status=403)

@superuser_required
def excel_root(request):
    """Root view for Excel app - redirects to file list"""
    return redirect('excel_file_handling:file_list')
