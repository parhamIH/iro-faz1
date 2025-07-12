# Excel File Handling App

این اپلیکیشن برای مدیریت و پردازش فایل‌های Excel طراحی شده است و از تمام مدل‌های فعلی سیستم پشتیبانی می‌کند.

## ویژگی‌ها

### مدل‌های پشتیبانی شده

1. **گروه‌های مشخصات** (`specification_groups`)
2. **مشخصات فنی** (`specifications`)
3. **برندها** (`brands`)
4. **دسته‌بندی‌ها** (`categories`)
5. **رنگ‌ها** (`colors`)
6. **گارانتی‌ها** (`warranties`)
7. **تگ‌ها** (`tags`)
8. **محصولات** (`products`)
9. **ویژگی‌های محصول** (`product_options`)
10. **مقادیر مشخصات محصول** (`product_specifications`)
11. **مقالات** (`articles`)
12. **دسته‌بندی‌های مقاله** (`article_categories`)

### قابلیت‌های اصلی

- آپلود فایل‌های Excel
- اعتبارسنجی فایل‌ها
- پردازش خودکار داده‌ها
- ثبت لاگ‌های کامل
- دانلود قالب‌های آماده
- پیش‌نمایش فایل‌ها
- مدیریت خطاها
- API endpoints

## نحوه استفاده

### 1. آپلود فایل

```python
# از طریق فرم وب
POST /excel/upload/

# از طریق API
POST /excel/api/upload/
{
    "file": "file.xlsx",
    "file_type": "products",
    "title": "محصولات جدید"
}
```

### 2. پردازش فایل

```python
# از طریق وب
GET /excel/files/{file_id}/process/

# از طریق API
POST /excel/api/files/{file_id}/process/
```

### 3. دانلود قالب

```python
GET /excel/templates/{file_type}/download/
```

## ساختار فایل‌های Excel

### گروه‌های مشخصات
| ستون | نوع | توضیح |
|------|-----|-------|
| name | string | نام گروه مشخصات |

### مشخصات فنی
| ستون | نوع | توضیح |
|------|-----|-------|
| name | string | نام مشخصه |
| data_type | string | نوع داده (int, decimal, str, bool) |
| unit | string | واحد اندازه‌گیری |
| is_main | boolean | آیا مشخصه اصلی است |
| group | string | نام گروه مشخصات |
| categories | string | دسته‌بندی‌ها (جدا شده با کاما) |

### برندها
| ستون | نوع | توضیح |
|------|-----|-------|
| name | string | نام برند |
| description | string | توضیحات |

### دسته‌بندی‌ها
| ستون | نوع | توضیح |
|------|-----|-------|
| name | string | نام دسته‌بندی |
| description | string | توضیحات |
| parent | string | نام دسته‌بندی والد |

### رنگ‌ها
| ستون | نوع | توضیح |
|------|-----|-------|
| name | string | نام رنگ |
| hex_code | string | کد رنگ (مثل #FF0000) |

### گارانتی‌ها
| ستون | نوع | توضیح |
|------|-----|-------|
| name | string | نام گارانتی |
| company | string | شرکت گارانتی |
| duration | integer | مدت گارانتی (ماه) |
| description | string | توضیحات |
| terms_conditions | string | شرایط و قوانین |
| support_phone | string | شماره تماس پشتیبانی |
| registration_required | boolean | نیاز به ثبت‌نام |

### تگ‌ها
| ستون | نوع | توضیح |
|------|-----|-------|
| name | string | نام تگ |

### محصولات
| ستون | نوع | توضیح |
|------|-----|-------|
| title | string | عنوان محصول |
| description | string | توضیحات |
| brand | string | نام برند |
| categories | string | دسته‌بندی‌ها (جدا شده با کاما) |
| tags | string | تگ‌ها (جدا شده با کاما) |
| is_active | boolean | فعال بودن |

### ویژگی‌های محصول
| ستون | نوع | توضیح |
|------|-----|-------|
| product | string | عنوان محصول |
| color | string | نام رنگ |
| warranty | string | نام گارانتی |
| option_price | decimal | قیمت |
| quantity | integer | تعداد موجودی |
| is_active | boolean | فعال بودن |
| is_active_discount | boolean | فعال بودن تخفیف |
| discount | decimal | درصد تخفیف |

### مقادیر مشخصات محصول
| ستون | نوع | توضیح |
|------|-----|-------|
| product | string | عنوان محصول |
| specification | string | نام مشخصه |
| int_value | integer | مقدار عددی |
| decimal_value | decimal | مقدار اعشاری |
| str_value | string | مقدار متنی |
| bool_value | boolean | مقدار منطقی |
| is_main | boolean | مشخصه اصلی |

### دسته‌بندی‌های مقاله
| ستون | نوع | توضیح |
|------|-----|-------|
| name | string | نام دسته‌بندی |

### مقالات
| ستون | نوع | توضیح |
|------|-----|-------|
| title | string | عنوان مقاله |
| content | string | محتوای مقاله |
| category | string | نام دسته‌بندی |
| tags | string | تگ‌ها (جدا شده با کاما) |
| is_published | boolean | منتشر شده |

## مدیریت خطاها

سیستم به طور کامل خطاها را مدیریت می‌کند:

- **خطاهای اعتبارسنجی**: بررسی نوع فایل، اندازه، و ساختار
- **خطاهای پردازش**: ثبت خطاهای هر ردیف به صورت جداگانه
- **خطاهای ارتباطی**: بررسی روابط بین مدل‌ها
- **لاگ‌های کامل**: ثبت تمام عملیات و خطاها

## API Endpoints

### آپلود فایل
```http
POST /excel/api/upload/
Content-Type: multipart/form-data

{
    "file": "file.xlsx",
    "file_type": "products",
    "title": "محصولات جدید"
}
```

### پردازش فایل
```http
POST /excel/api/files/{file_id}/process/
```

### پاسخ‌های API
```json
{
    "success": true,
    "file_id": 1,
    "message": "فایل با موفقیت آپلود شد"
}
```

## تنظیمات

### محدودیت‌های فایل
- حداکثر اندازه: 10 مگابایت
- فرمت‌های مجاز: .xlsx, .xls

### تنظیمات پردازش
- پردازش تراکنشی: هر ردیف در یک تراکنش جداگانه
- مدیریت خطا: ادامه پردازش در صورت خطا در یک ردیف
- لاگ‌گیری: ثبت تمام عملیات

## مثال‌های استفاده

### ایجاد فایل Excel با pandas
```python
import pandas as pd

# ایجاد داده‌های نمونه
data = {
    'name': ['سامسونگ', 'اپل', 'شیائومی'],
    'description': ['برند کره‌ای', 'برند آمریکایی', 'برند چینی']
}

df = pd.DataFrame(data)

# ذخیره فایل
df.to_excel('brands.xlsx', index=False)
```

### پردازش فایل با API
```python
import requests

# آپلود فایل
with open('brands.xlsx', 'rb') as f:
    files = {'file': f}
    data = {'file_type': 'brands', 'title': 'برندهای جدید'}
    response = requests.post('/excel/api/upload/', files=files, data=data)

file_id = response.json()['file_id']

# پردازش فایل
response = requests.post(f'/excel/api/files/{file_id}/process/')
```

## نکات مهم

1. **ترتیب پردازش**: ابتدا مدل‌های پایه (برندها، دسته‌بندی‌ها، و...) سپس مدل‌های وابسته
2. **اعتبارسنجی**: تمام فیلدهای اجباری بررسی می‌شوند
3. **روابط**: روابط بین مدل‌ها به درستی مدیریت می‌شوند
4. **عملکرد**: پردازش بهینه برای فایل‌های بزرگ
5. **امنیت**: بررسی نوع فایل و اندازه برای جلوگیری از حملات

## عیب‌یابی

### خطاهای رایج

1. **فایل نامعتبر**: بررسی فرمت و اندازه فایل
2. **ستون‌های ناموجود**: اطمینان از وجود ستون‌های اجباری
3. **داده‌های نامعتبر**: بررسی نوع داده‌ها
4. **روابط ناموجود**: اطمینان از وجود مدل‌های مرتبط

### لاگ‌ها

تمام عملیات در جدول `ExcelImportLog` ثبت می‌شوند:
- سطح: info, warning, error, success
- شماره ردیف: برای شناسایی خطاها
- پیام: توضیح کامل عملیات 