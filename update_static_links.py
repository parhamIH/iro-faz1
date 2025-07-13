#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت به‌روزرسانی لینک‌های media به static در فایل sample_files.html
"""

import re

def update_static_links():
    """به‌روزرسانی لینک‌های media به static"""
    
    file_path = 'excel_file_handling/templates/excel_file_handling/sample_files.html'
    
    # خواندن فایل
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # جایگزینی لینک‌های media با static
    # الگوی regex برای پیدا کردن لینک‌های media
    pattern = r'href="/media/samples/excel_templates/([^"]+)"'
    replacement = r'href="{% static \'samples/excel_templates/\1\' %}"'
    
    # اعمال جایگزینی
    updated_content = re.sub(pattern, replacement, content)
    
    # نوشتن فایل به‌روزرسانی شده
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ تمام لینک‌های media به static به‌روزرسانی شدند!")

if __name__ == "__main__":
    update_static_links() 