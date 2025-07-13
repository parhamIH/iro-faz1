from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import json
import pandas as pd
from .models import ExcelFile, ExcelImportLog
from .services import ExcelImportService
from .forms import ExcelFileUploadForm
from store.models import (
    Product, Category, Brand, Specification, ProductSpecification,
    Color, Warranty, Tag, SpecificationGroup, ProductOption,
    Article, ArticleCategory
)

@login_required
def upload_excel(request):
    """صفحه آپلود فایل Excel"""
    if request.method == 'POST':
        form = ExcelFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.save(commit=False)
            excel_file.save()
            
            messages.success(request, f'فایل {excel_file.title} با موفقیت آپلود شد')
            return redirect('excel_file_handling:file_list')
    else:
        form = ExcelFileUploadForm()
    
    # آمار کلی
    total_files = ExcelFile.objects.count()
    pending_files = ExcelFile.objects.filter(status='pending').count()
    completed_files = ExcelFile.objects.filter(status='completed').count()
    failed_files = ExcelFile.objects.filter(status='failed').count()
    
    context = {
        'form': form,
        'total_files': total_files,
        'pending_files': pending_files,
        'completed_files': completed_files,
        'failed_files': failed_files,
    }
    
    return render(request, 'excel_file_handling/upload.html', context)

@login_required
def file_list(request):
    """لیست فایل‌های Excel"""
    files = ExcelFile.objects.all().order_by('-uploaded_at')
    
    # فیلتر کردن
    file_type = request.GET.get('file_type')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if file_type:
        files = files.filter(file_type=file_type)
    if status:
        files = files.filter(status=status)
    if search:
        files = files.filter(
            Q(title__icontains=search) | 
            Q(file__name__icontains=search)
        )
    
    # صفحه‌بندی
    paginator = Paginator(files, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'file_types': ExcelFile.FILE_TYPE_CHOICES,
        'status_choices': ExcelFile.STATUS_CHOICES,
        'current_filters': {
            'file_type': file_type,
            'status': status,
            'search': search,
        }
    }
    
    return render(request, 'excel_file_handling/file_list.html', context)

@login_required
def file_detail(request, file_id):
    """جزئیات فایل Excel"""
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    logs = ExcelImportLog.objects.filter(excel_file=excel_file).order_by('-created_at')
    
    # آمار لاگ‌ها
    log_stats = {
        'total': logs.count(),
        'info': logs.filter(level='info').count(),
        'warning': logs.filter(level='warning').count(),
        'error': logs.filter(level='error').count(),
        'success': logs.filter(level='success').count(),
    }
    
    context = {
        'excel_file': excel_file,
        'logs': logs[:100],  # فقط 100 لاگ آخر
        'log_stats': log_stats,
    }
    
    return render(request, 'excel_file_handling/file_detail.html', context)

@login_required
def process_file(request, file_id):
    """پردازش فایل Excel"""
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    
    if excel_file.status != 'pending':
        messages.warning(request, f'فایل در وضعیت {excel_file.get_status_display()} است')
        return redirect('excel_file_handling:file_detail', file_id=file_id)
    
    try:
        service = ExcelImportService(file_id)
        service.process_file()
        messages.success(request, f'فایل {excel_file.title} با موفقیت پردازش شد')
    except Exception as e:
        messages.error(request, f'خطا در پردازش فایل: {str(e)}')
    
    return redirect('excel_file_handling:file_detail', file_id=file_id)

@login_required
def delete_file(request, file_id):
    """حذف فایل Excel"""
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    
    if request.method == 'POST':
        title = excel_file.title
        excel_file.delete()
        messages.success(request, f'فایل {title} حذف شد')
        return redirect('excel_file_handling:file_list')
    
    return render(request, 'excel_file_handling/delete_confirm.html', {'excel_file': excel_file})

@login_required
def download_template(request, file_type):
    """دانلود قالب Excel"""
    templates = {
        'brands': {
            'columns': ['name', 'description'],
            'sample_data': [
                ['سامسونگ', 'برند معتبر کره‌ای'],
                ['اپل', 'برند آمریکایی'],
                ['شیائومی', 'برند چینی'],
            ]
        },
        'categories': {
            'columns': ['name', 'description', 'parent'],
            'sample_data': [
                ['موبایل', 'گوشی‌های هوشمند', ''],
                ['لپ‌تاپ', 'کامپیوترهای قابل حمل', ''],
                ['گوشی هوشمند', 'گوشی‌های پیشرفته', 'موبایل'],
            ]
        },
        'colors': {
            'columns': ['name', 'hex_code'],
            'sample_data': [
                ['قرمز', '#FF0000'],
                ['آبی', '#0000FF'],
                ['سبز', '#00FF00'],
            ]
        },
        'warranties': {
            'columns': ['name', 'company', 'duration', 'description', 'terms_conditions', 'support_phone', 'registration_required'],
            'sample_data': [
                ['گارانتی 1 ساله', 'شرکت گارانتی', 12, 'گارانتی کامل', 'شرایط و قوانین', '02112345678', True],
            ]
        },
        'specification_groups': {
            'columns': ['name'],
            'sample_data': [
                ['مشخصات فنی'],
                ['مشخصات ظاهری'],
                ['مشخصات نرم‌افزاری'],
            ]
        },
        'specifications': {
            'columns': ['name', 'data_type', 'unit', 'is_main', 'group', 'categories'],
            'sample_data': [
                ['رزولوشن', 'str', 'پیکسل', True, 'مشخصات فنی', 'موبایل,لپ‌تاپ'],
                ['حافظه', 'int', 'GB', True, 'مشخصات فنی', 'موبایل,لپ‌تاپ'],
                ['وزن', 'decimal', 'گرم', False, 'مشخصات ظاهری', 'موبایل,لپ‌تاپ'],
            ]
        },
        'tags': {
            'columns': ['name'],
            'sample_data': [
                ['جدید'],
                ['پرفروش'],
                ['تخفیف'],
            ]
        },
        'products': {
            'columns': ['title', 'description', 'brand', 'categories', 'tags', 'is_active'],
            'sample_data': [
                ['گوشی سامسونگ Galaxy S21', 'گوشی هوشمند پیشرفته', 'سامسونگ', 'موبایل,گوشی هوشمند', 'جدید,پرفروش', True],
            ]
        },
        'product_options': {
            'columns': ['product', 'color', 'warranty', 'option_price', 'quantity', 'is_active', 'is_active_discount', 'discount'],
            'sample_data': [
                ['گوشی سامسونگ Galaxy S21', 'قرمز', 'گارانتی 1 ساله', 15000000, 10, True, False, 0],
            ]
        },
        'product_specifications': {
            'columns': ['product', 'specification', 'int_value', 'decimal_value', 'str_value', 'bool_value', 'is_main'],
            'sample_data': [
                ['گوشی سامسونگ Galaxy S21', 'رزولوشن', None, None, '1080x2400', None, True],
                ['گوشی سامسونگ Galaxy S21', 'حافظه', 128, None, None, None, True],
            ]
        },
        'article_categories': {
            'columns': ['name'],
            'sample_data': [
                ['اخبار تکنولوژی'],
                ['راهنمای خرید'],
                ['بررسی محصولات'],
            ]
        },
        'articles': {
            'columns': ['title', 'content', 'category', 'tags', 'is_published'],
            'sample_data': [
                ['راهنمای خرید گوشی هوشمند', 'محتوای مقاله...', 'راهنمای خرید', 'جدید,پرفروش', True],
            ]
        },
    }
    
    if file_type not in templates:
        messages.error(request, 'نوع فایل نامعتبر است')
        return redirect('excel_file_handling:upload_excel')
    
    template = templates[file_type]
    
    # ایجاد DataFrame
    df = pd.DataFrame(template['sample_data'], columns=template['columns'])
    
    # ایجاد فایل Excel
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Template', index=False)
    
    output.seek(0)
    
    # نام فایل
    filename = f'template_{file_type}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
def preview_file(request, file_id):
    """پیش‌نمایش فایل Excel"""
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    
    try:
        df = pd.read_excel(excel_file.file.path)
        preview_data = df.head(10).to_dict('records')  # 10 ردیف اول
        columns = df.columns.tolist()
        
        context = {
            'excel_file': excel_file,
            'preview_data': preview_data,
            'columns': columns,
            'total_rows': len(df),
        }
        
        return render(request, 'excel_file_handling/preview.html', context)
        
    except Exception as e:
        messages.error(request, f'خطا در خواندن فایل: {str(e)}')
        return redirect('excel_file_handling:file_detail', file_id=file_id)

@login_required
def dashboard(request):
    """داشبورد کلی"""
    # آمار فایل‌ها
    total_files = ExcelFile.objects.count()
    pending_files = ExcelFile.objects.filter(status='pending').count()
    completed_files = ExcelFile.objects.filter(status='completed').count()
    failed_files = ExcelFile.objects.filter(status='failed').count()
    
    # آمار بر اساس نوع فایل
    file_type_stats = {}
    for file_type, label in ExcelFile.FILE_TYPE_CHOICES:
        count = ExcelFile.objects.filter(file_type=file_type).count()
        if count > 0:
            file_type_stats[label] = count
    
    # آخرین فایل‌ها
    recent_files = ExcelFile.objects.all().order_by('-uploaded_at')[:5]
    
    # آخرین لاگ‌ها
    recent_logs = ExcelImportLog.objects.all().order_by('-created_at')[:10]
    
    # آمار مدل‌ها
    model_stats = {
        'products': Product.objects.count(),
        'categories': Category.objects.count(),
        'brands': Brand.objects.count(),
        'specifications': Specification.objects.count(),
        'specification_groups': SpecificationGroup.objects.count(),
        'colors': Color.objects.count(),
        'warranties': Warranty.objects.count(),
        'tags': Tag.objects.count(),
        'articles': Article.objects.count(),
        'article_categories': ArticleCategory.objects.count(),
    }
    
    context = {
        'total_files': total_files,
        'pending_files': pending_files,
        'completed_files': completed_files,
        'failed_files': failed_files,
        'file_type_stats': file_type_stats,
        'recent_files': recent_files,
        'recent_logs': recent_logs,
        'model_stats': model_stats,
    }
    
    return render(request, 'excel_file_handling/dashboard.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def api_upload_file(request):
    """API برای آپلود فایل"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'فایل ارسال نشده'}, status=400)
        
        file = request.FILES['file']
        file_type = request.POST.get('file_type')
        title = request.POST.get('title', file.name)
        
        if not file_type:
            return JsonResponse({'error': 'نوع فایل مشخص نشده'}, status=400)
        
        # بررسی نوع فایل
        if file_type not in dict(ExcelFile.FILE_TYPE_CHOICES):
            return JsonResponse({'error': 'نوع فایل نامعتبر'}, status=400)
        
        # ایجاد فایل
        excel_file = ExcelFile.objects.create(
            title=title,
            file=file,
            file_type=file_type
        )
        
        return JsonResponse({
            'success': True,
            'file_id': excel_file.id,
            'message': 'فایل با موفقیت آپلود شد'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_process_file(request, file_id):
    """API برای پردازش فایل"""
    try:
        excel_file = get_object_or_404(ExcelFile, id=file_id)
        
        if excel_file.status != 'pending':
            return JsonResponse({'error': 'فایل در وضعیت پردازش نیست'}, status=400)
        
        service = ExcelImportService(file_id)
        service.process_file()
        
        return JsonResponse({
            'success': True,
            'message': 'فایل با موفقیت پردازش شد'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def sample_files(request):
    """نمایش صفحه فایل‌های نمونه"""
    return render(request, 'excel_file_handling/sample_files.html')
