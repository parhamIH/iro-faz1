#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت ایجاد فایل‌های Excel نمونه برای سیستم مدیریت فایل‌های Excel
"""

import pandas as pd
import os
from datetime import datetime

def create_sample_excel_files():
    """ایجاد فایل‌های Excel نمونه برای تمام انواع پشتیبانی شده"""
    
    # تعریف قالب‌ها و داده‌های نمونه
    templates = {
        'brands': {
            'columns': ['name', 'description'],
            'sample_data': [
                ['سامسونگ', 'برند معتبر کره‌ای در زمینه الکترونیک'],
                ['اپل', 'برند آمریکایی پیشرو در تکنولوژی'],
                ['شیائومی', 'برند چینی با کیفیت بالا و قیمت مناسب'],
                ['هوآوی', 'برند چینی پیشرو در تکنولوژی ارتباطات'],
                ['لنوو', 'برند چینی در زمینه کامپیوتر و لپ‌تاپ'],
                ['ایسوس', 'برند تایوانی در زمینه کامپیوتر و قطعات'],
                ['اچ‌پی', 'برند آمریکایی در زمینه کامپیوتر و پرینتر'],
                ['دل', 'برند آمریکایی در زمینه کامپیوتر و سرور'],
            ]
        },
        'categories': {
            'columns': ['name', 'description', 'parent'],
            'sample_data': [
                ['الکترونیک', 'محصولات الکترونیکی', ''],
                ['کامپیوتر', 'محصولات کامپیوتری', ''],
                ['موبایل', 'گوشی‌های هوشمند', 'الکترونیک'],
                ['لپ‌تاپ', 'کامپیوترهای قابل حمل', 'کامپیوتر'],
                ['دسکتاپ', 'کامپیوترهای رومیزی', 'کامپیوتر'],
                ['تبلت', 'تبلت‌های هوشمند', 'الکترونیک'],
                ['لوازم جانبی', 'لوازم جانبی کامپیوتر و موبایل', ''],
                ['کابل و شارژر', 'کابل‌ها و شارژرهای مختلف', 'لوازم جانبی'],
                ['کیف و کاور', 'کیف‌ها و کاورهای محافظ', 'لوازم جانبی'],
            ]
        },
        'colors': {
            'columns': ['name', 'hex_code'],
            'sample_data': [
                ['قرمز', '#FF0000'],
                ['آبی', '#0000FF'],
                ['سبز', '#00FF00'],
                ['زرد', '#FFFF00'],
                ['مشکی', '#000000'],
                ['سفید', '#FFFFFF'],
                ['خاکستری', '#808080'],
                ['نارنجی', '#FFA500'],
                ['بنفش', '#800080'],
                ['صورتی', '#FFC0CB'],
            ]
        },
        'warranties': {
            'columns': ['name', 'company', 'duration', 'description', 'terms_conditions', 'support_phone', 'registration_required'],
            'sample_data': [
                ['گارانتی 1 ساله', 'شرکت گارانتی ایران', 12, 'گارانتی کامل قطعات و کار', 'شرایط و قوانین گارانتی', '02112345678', True],
                ['گارانتی 2 ساله', 'مرکز خدمات پس از فروش', 24, 'گارانتی تمدید شده', 'شرایط ویژه گارانتی 2 ساله', '02187654321', False],
                ['گارانتی 6 ماهه', 'نمایندگی رسمی', 6, 'گارانتی محدود', 'شرایط گارانتی 6 ماهه', '02111111111', True],
                ['گارانتی 3 ساله', 'شرکت اصلی', 36, 'گارانتی طلایی', 'شرایط گارانتی طلایی', '02122222222', True],
            ]
        },
        'specification_groups': {
            'columns': ['name'],
            'sample_data': [
                ['مشخصات فنی'],
                ['مشخصات ظاهری'],
                ['مشخصات نرم‌افزاری'],
                ['مشخصات امنیتی'],
                ['مشخصات ارتباطی'],
                ['مشخصات صوتی و تصویری'],
                ['مشخصات باتری و شارژ'],
                ['مشخصات اتصالات'],
            ]
        },
        'specifications': {
            'columns': ['name', 'data_type', 'unit', 'is_main', 'group', 'categories'],
            'sample_data': [
                ['رزولوشن', 'str', 'پیکسل', True, 'مشخصات فنی', 'موبایل,لپ‌تاپ,تبلت'],
                ['حافظه', 'int', 'GB', True, 'مشخصات فنی', 'موبایل,لپ‌تاپ,دسکتاپ'],
                ['وزن', 'decimal', 'گرم', False, 'مشخصات ظاهری', 'موبایل,لپ‌تاپ,تبلت'],
                ['اندازه صفحه', 'decimal', 'اینچ', True, 'مشخصات ظاهری', 'موبایل,لپ‌تاپ,تبلت'],
                ['سیستم عامل', 'str', '', True, 'مشخصات نرم‌افزاری', 'موبایل,لپ‌تاپ,تبلت'],
                ['پردازنده', 'str', '', True, 'مشخصات فنی', 'لپ‌تاپ,دسکتاپ'],
                ['دوربین', 'str', 'مگاپیکسل', False, 'مشخصات فنی', 'موبایل,تبلت'],
                ['باتری', 'int', 'mAh', False, 'مشخصات فنی', 'موبایل,تبلت'],
                ['رنگ', 'str', '', False, 'مشخصات ظاهری', 'موبایل,لپ‌تاپ,تبلت'],
                ['مقاوم در برابر آب', 'bool', '', False, 'مشخصات امنیتی', 'موبایل'],
            ]
        },
        'tags': {
            'columns': ['name'],
            'sample_data': [
                ['جدید'],
                ['پرفروش'],
                ['تخفیف'],
                ['پیشنهاد ویژه'],
                ['محصول برتر'],
                ['محبوب'],
                ['کیفیت بالا'],
                ['قیمت مناسب'],
                ['ارسال رایگان'],
                ['ضمانت اصالت'],
            ]
        },
        'products': {
            'columns': ['title', 'description', 'brand', 'categories', 'tags', 'is_active'],
            'sample_data': [
                ['گوشی سامسونگ Galaxy S21', 'گوشی هوشمند پیشرفته با دوربین حرفه‌ای', 'سامسونگ', 'موبایل', 'جدید,پرفروش', True],
                ['لپ‌تاپ اپل MacBook Pro', 'لپ‌تاپ حرفه‌ای برای کارهای گرافیکی', 'اپل', 'لپ‌تاپ', 'محصول برتر,کیفیت بالا', True],
                ['تبلت شیائومی Mi Pad', 'تبلت با قیمت مناسب و کیفیت بالا', 'شیائومی', 'تبلت', 'قیمت مناسب,محبوب', True],
                ['کامپیوتر دسکتاپ لنوو', 'کامپیوتر رومیزی برای کارهای اداری', 'لنوو', 'دسکتاپ', 'قیمت مناسب', True],
                ['گوشی هوآوی P40 Pro', 'گوشی هوشمند با دوربین پیشرفته', 'هوآوی', 'موبایل', 'جدید,کیفیت بالا', True],
                ['لپ‌تاپ ایسوس ROG', 'لپ‌تاپ گیمینگ با کارت گرافیک قوی', 'ایسوس', 'لپ‌تاپ', 'محصول برتر,پرفروش', True],
                ['کابل شارژ سریع', 'کابل USB-C با قابلیت شارژ سریع', '', 'کابل و شارژر', 'ارسال رایگان', True],
                ['کیف محافظ لپ‌تاپ', 'کیف محافظ با کیفیت بالا', '', 'کیف و کاور', 'ضمانت اصالت', True],
            ]
        },
        'product_options': {
            'columns': ['product', 'color', 'warranty', 'option_price', 'quantity', 'is_active', 'is_active_discount', 'discount'],
            'sample_data': [
                ['گوشی سامسونگ Galaxy S21', 'مشکی', 'گارانتی 1 ساله', 15000000, 10, True, False, 0],
                ['گوشی سامسونگ Galaxy S21', 'سفید', 'گارانتی 1 ساله', 15000000, 5, True, True, 10],
                ['لپ‌تاپ اپل MacBook Pro', 'خاکستری', 'گارانتی 2 ساله', 85000000, 3, True, False, 0],
                ['تبلت شیائومی Mi Pad', 'سفید', 'گارانتی 1 ساله', 12000000, 15, True, True, 15],
                ['کامپیوتر دسکتاپ لنوو', 'مشکی', 'گارانتی 1 ساله', 25000000, 8, True, False, 0],
                ['گوشی هوآوی P40 Pro', 'آبی', 'گارانتی 2 ساله', 18000000, 7, True, True, 5],
            ]
        },
        'product_specifications': {
            'columns': ['product', 'specification', 'int_value', 'decimal_value', 'str_value', 'bool_value', 'is_main'],
            'sample_data': [
                ['گوشی سامسونگ Galaxy S21', 'رزولوشن', None, None, '1080x2400', None, True],
                ['گوشی سامسونگ Galaxy S21', 'حافظه', 128, None, None, None, True],
                ['گوشی سامسونگ Galaxy S21', 'وزن', None, 169.0, None, None, False],
                ['لپ‌تاپ اپل MacBook Pro', 'رزولوشن', None, None, '2560x1600', None, True],
                ['لپ‌تاپ اپل MacBook Pro', 'حافظه', 512, None, None, None, True],
                ['لپ‌تاپ اپل MacBook Pro', 'وزن', None, 1400.0, None, None, False],
                ['تبلت شیائومی Mi Pad', 'اندازه صفحه', None, 10.1, None, None, True],
                ['تبلت شیائومی Mi Pad', 'حافظه', 64, None, None, None, True],
            ]
        },
        'article_categories': {
            'columns': ['name'],
            'sample_data': [
                ['اخبار تکنولوژی'],
                ['راهنمای خرید'],
                ['بررسی محصولات'],
                ['آموزش و ترفندها'],
                ['مقایسه محصولات'],
                ['اخبار برندها'],
                ['نکات نگهداری'],
                ['حل مشکلات'],
            ]
        },
        'articles': {
            'columns': ['title', 'content', 'category', 'tags', 'is_published'],
            'sample_data': [
                ['راهنمای خرید گوشی هوشمند', 'در این مقاله به شما کمک می‌کنیم تا بهترین گوشی هوشمند را انتخاب کنید...', 'راهنمای خرید', 'جدید,پرفروش', True],
                ['مقایسه لپ‌تاپ‌های گیمینگ', 'مقایسه کامل لپ‌تاپ‌های گیمینگ موجود در بازار...', 'مقایسه محصولات', 'محصول برتر', True],
                ['نکات نگهداری از باتری موبایل', 'چگونه باتری موبایل خود را سالم نگه دارید...', 'نکات نگهداری', 'کیفیت بالا', True],
                ['بررسی گوشی سامسونگ Galaxy S21', 'بررسی کامل گوشی جدید سامسونگ...', 'بررسی محصولات', 'جدید', True],
                ['اخبار جدید اپل', 'آخرین اخبار و محصولات شرکت اپل...', 'اخبار برندها', 'محصول برتر', True],
            ]
        },
    }
    
    # ایجاد پوشه خروجی
    output_dir = 'samples/excel_templates'
    os.makedirs(output_dir, exist_ok=True)
    
    print("در حال ایجاد فایل‌های Excel نمونه...")
    
    # ایجاد فایل‌های نمونه
    for file_type, template in templates.items():
        try:
            # ایجاد DataFrame
            df = pd.DataFrame(template['sample_data'], columns=template['columns'])
            
            # نام فایل
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'sample_{file_type}_{timestamp}.xlsx'
            filepath = os.path.join(output_dir, filename)
            
            # ذخیره فایل Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Template', index=False)
                
                # اضافه کردن راهنما
                guide_data = {
                    'ستون': template['columns'],
                    'توضیحات': [
                        'نام برند (اجباری)' if col == 'name' and file_type == 'brands' else
                        'توضیحات برند (اختیاری)' if col == 'description' and file_type == 'brands' else
                        'نام دسته‌بندی (اجباری)' if col == 'name' and file_type == 'categories' else
                        'توضیحات (اختیاری)' if col == 'description' and file_type == 'categories' else
                        'نام دسته‌بندی والد (اختیاری)' if col == 'parent' else
                        'نام رنگ (اجباری)' if col == 'name' and file_type == 'colors' else
                        'کد رنگ مثل #FF0000 (اختیاری)' if col == 'hex_code' else
                        'نام گارانتی (اجباری)' if col == 'name' and file_type == 'warranties' else
                        'شرکت گارانتی (اختیاری)' if col == 'company' else
                        'مدت گارانتی به ماه (اختیاری)' if col == 'duration' else
                        'توضیحات (اختیاری)' if col == 'description' and file_type == 'warranties' else
                        'شرایط و قوانین (اختیاری)' if col == 'terms_conditions' else
                        'شماره تماس پشتیبانی (اختیاری)' if col == 'support_phone' else
                        'نیاز به ثبت‌نام (true/false)' if col == 'registration_required' else
                        'نام گروه مشخصات (اجباری)' if col == 'name' and file_type == 'specification_groups' else
                        'نام مشخصه (اجباری)' if col == 'name' and file_type == 'specifications' else
                        'نوع داده: int, decimal, str, bool (اجباری)' if col == 'data_type' else
                        'واحد اندازه‌گیری (اختیاری)' if col == 'unit' else
                        'آیا مشخصه اصلی است (true/false)' if col == 'is_main' else
                        'نام گروه مشخصات (اختیاری)' if col == 'group' else
                        'دسته‌بندی‌ها (جدا شده با کاما)' if col == 'categories' else
                        'نام تگ (اجباری)' if col == 'name' and file_type == 'tags' else
                        'عنوان محصول (اجباری)' if col == 'title' else
                        'توضیحات محصول (اختیاری)' if col == 'description' and file_type == 'products' else
                        'نام برند (اختیاری)' if col == 'brand' else
                        'دسته‌بندی‌ها (جدا شده با کاما)' if col == 'categories' and file_type == 'products' else
                        'تگ‌ها (جدا شده با کاما)' if col == 'tags' and file_type == 'products' else
                        'فعال بودن (true/false)' if col == 'is_active' else
                        'عنوان محصول (اجباری)' if col == 'product' else
                        'نام رنگ (اختیاری)' if col == 'color' else
                        'نام گارانتی (اختیاری)' if col == 'warranty' else
                        'قیمت (اختیاری)' if col == 'option_price' else
                        'تعداد موجودی (اختیاری)' if col == 'quantity' else
                        'فعال بودن تخفیف (true/false)' if col == 'is_active_discount' else
                        'درصد تخفیف (اختیاری)' if col == 'discount' else
                        'مشخصه (اجباری)' if col == 'specification' else
                        'مقدار عددی صحیح (اختیاری)' if col == 'int_value' else
                        'مقدار اعشاری (اختیاری)' if col == 'decimal_value' else
                        'مقدار متنی (اختیاری)' if col == 'str_value' else
                        'مقدار منطقی (اختیاری)' if col == 'bool_value' else
                        'عنوان مقاله (اجباری)' if col == 'title' and file_type == 'articles' else
                        'محتوای مقاله (اجباری)' if col == 'content' else
                        'نام دسته‌بندی (اختیاری)' if col == 'category' else
                        'تگ‌ها (جدا شده با کاما)' if col == 'tags' and file_type == 'articles' else
                        'منتشر شده (true/false)' if col == 'is_published' else
                        'نام دسته‌بندی مقاله (اجباری)' if col == 'name' and file_type == 'article_categories' else
                        'نام دسته‌بندی (اجباری)' if col == 'name' and file_type == 'article_categories' else
                        'نام (اجباری)' for col in template['columns']
                    ]
                }
                
                guide_df = pd.DataFrame(guide_data)
                guide_df.to_excel(writer, sheet_name='راهنما', index=False)
            
            print(f"✅ فایل {filename} ایجاد شد")
            
        except Exception as e:
            print(f"❌ خطا در ایجاد فایل {file_type}: {str(e)}")
    
    print(f"\n🎉 تمام فایل‌های نمونه در پوشه {output_dir} ایجاد شدند!")
    print(f"📁 مسیر کامل: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    create_sample_excel_files() 