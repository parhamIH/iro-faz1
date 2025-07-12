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
        file = self.cleaned_data.get('file')
        if file:
            # بررسی اندازه فایل (حداکثر 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('حجم فایل نباید بیشتر از 10 مگابایت باشد.')
            
            # بررسی نوع فایل
            allowed_extensions = ['.xlsx', '.xls']
            file_extension = file.name.lower()
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError('فقط فایل‌های Excel (.xlsx, .xls) مجاز هستند.')
        
        return file
    
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        file_type = cleaned_data.get('file_type')
        
        if file and file_type:
            # بررسی تطابق نوع فایل با محتوای آن (اختیاری)
            pass
        
        return cleaned_data 