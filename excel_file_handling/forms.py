from django import forms
from .models import ExcelFile

class ExcelFileUploadForm(forms.ModelForm):
    """فرم آپلود فایل Excel"""
    
    class Meta:
        model = ExcelFile
        fields = ['title', 'file', 'file_type']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان فایل را وارد کنید'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.xlsx,.xls'
            }),
            'file_type': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def clean_file(self):
        """اعتبارسنجی فایل"""
        file = self.cleaned_data.get('file')
        if file:
            # بررسی پسوند فایل
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError('فقط فایل‌های Excel (.xlsx, .xls) قابل قبول هستند')
            
            # بررسی اندازه فایل (حداکثر 10 مگابایت)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('حجم فایل نباید بیشتر از 10 مگابایت باشد')
        
        return file
    
    def clean(self):
        """اعتبارسنجی کلی فرم"""
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        file_type = cleaned_data.get('file_type')
        
        if file and file_type:
            # بررسی سازگاری نوع فایل با نام فایل
            file_name = file.name.lower()
            
            # بررسی اینکه آیا فایل حاوی داده‌های مناسب برای نوع انتخاب شده است
            if file_type == 'products' and 'product' not in file_name:
                self.add_warning('file', 'نام فایل با نوع انتخاب شده مطابقت ندارد')
            elif file_type == 'categories' and 'category' not in file_name:
                self.add_warning('file', 'نام فایل با نوع انتخاب شده مطابقت ندارد')
            elif file_type == 'brands' and 'brand' not in file_name:
                self.add_warning('file', 'نام فایل با نوع انتخاب شده مطابقت ندارد')
        
        return cleaned_data

class ExcelFileFilterForm(forms.Form):
    """فرم فیلتر کردن فایل‌های Excel"""
    
    file_type = forms.ChoiceField(
        choices=[('', 'همه انواع')] + ExcelFile.FILE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'همه وضعیت‌ها')] + ExcelFile.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'جستجو در عنوان یا نام فایل...'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

class ExcelFileBulkActionForm(forms.Form):
    """فرم عملیات گروهی روی فایل‌ها"""
    
    ACTION_CHOICES = [
        ('process', 'پردازش فایل‌های انتخاب شده'),
        ('delete', 'حذف فایل‌های انتخاب شده'),
        ('download_logs', 'دانلود لاگ‌های فایل‌های انتخاب شده'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    file_ids = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def clean_file_ids(self):
        """اعتبارسنجی شناسه‌های فایل"""
        file_ids = self.cleaned_data.get('file_ids')
        if file_ids:
            try:
                ids = [int(id.strip()) for id in file_ids.split(',') if id.strip()]
                return ids
            except ValueError:
                raise forms.ValidationError('شناسه‌های فایل نامعتبر هستند')
        return []

class ExcelFileValidationForm(forms.Form):
    """فرم اعتبارسنجی فایل Excel قبل از آپلود"""
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        })
    )
    
    file_type = forms.ChoiceField(
        choices=ExcelFile.FILE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean_file(self):
        """اعتبارسنجی فایل"""
        file = self.cleaned_data.get('file')
        if file:
            # بررسی پسوند فایل
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError('فقط فایل‌های Excel (.xlsx, .xls) قابل قبول هستند')
            
            # بررسی اندازه فایل (حداکثر 10 مگابایت)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('حجم فایل نباید بیشتر از 10 مگابایت باشد')
        
        return file 