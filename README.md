# IRO Final Project

این پروژه یک سیستم مدیریت کاربران با دو نقش اصلی Admin و Provider می‌باشد.

## ویژگی‌ها

- سیستم احراز هویت کاربران
- مدیریت سطوح دسترسی (Admin و Provider)
- پروفایل کاربری با اطلاعات تکمیلی
- سیستم آدرس‌دهی
- سیستم اعلان‌ها
- داشبوردهای مجزا برای Admin و Provider

## نیازمندی‌ها

- Python 3.8+
- Django 4.0+
- Django REST Framework

## نصب و راه‌اندازی

1. کلون کردن پروژه:
```bash
git clone https://github.com/YOUR_USERNAME/iro-finalproject.git
cd iro-finalproject
```

2. ساخت محیط مجازی:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. نصب وابستگی‌ها:
```bash
pip install -r requirements.txt
```

4. اجرای مایگریشن‌ها:
```bash
python manage.py migrate
```

5. ساخت یک کاربر ادمین:
```bash
python manage.py createsuperuser
```

6. اجرای سرور توسعه:
```bash
python manage.py runserver
```

## ساختار پروژه

- `accounts/`: اپلیکیشن مدیریت کاربران
  - `models.py`: مدل‌های کاربری، پروفایل، آدرس و اعلان‌ها
  - `views.py`: ویوهای مربوط به مدیریت کاربران
  - `permissions.py`: کلاس‌های مجوز دسترسی
  - `serializers.py`: سریالایزرهای API

## API Endpoints

- `/api/admin/dashboard/`: داشبورد مدیر سیستم
- `/api/provider/dashboard/`: داشبورد ارائه‌دهنده
- `/api/staff/dashboard/`: داشبورد مشترک

## مجوزهای دسترسی

- **Admin**: دسترسی کامل به تمام بخش‌ها
- **Provider**: دسترسی محدود به بخش‌های مرتبط با ارائه‌دهنده
- **Staff**: دسترسی به بخش‌های مشترک

## مشارکت

1. Fork کردن پروژه
2. ساخت برنچ برای ویژگی جدید
3. Commit کردن تغییرات
4. Push به برنچ
5. ارسال Pull Request

## لایسنس

This project is licensed under the MIT License - see the LICENSE file for details. 

## فیلترهای API فروشگاه (Store API Filters)

در این بخش، فیلترهای قابل استفاده برای هر مدل و نحوه استفاده از آن‌ها در URL آورده شده است.

### فیلترهای قدیمی (قبل از توسعه جدید)

#### محصولات (Product)

- جستجو: `/api/products/?search=کلمه`
- دسته‌بندی: `/api/products/?categories=1` (آیدی دسته)
- برند: `/api/products/?brand=1`
- تگ: `/api/products/?tags=1`
- رنگ: `/api/products/?options__color=1`
- فعال بودن: `/api/products/?is_active=true`

#### دسته‌بندی (Category)

- جستجو: `/api/categories/?search=کلمه`
- والد: `/api/categories/?parent=1`
- برند: `/api/categories/?brand=1`

#### ویژگی محصول (ProductOption)

- محصول: `/api/product-options/?product=1`
- رنگ: `/api/product-options/?color=1`
- فعال بودن: `/api/product-options/?is_active=true`

---

### فیلترهای جدید (پس از توسعه)

#### محصولات (Product)

- جستجو: `/api/products/?search=کلمه`
- دسته‌بندی: `/api/products/?categories=1,2,3` (چندتایی)
- برند: `/api/products/?brands=1,2`
- تگ: `/api/products/?tags=1,2`
- رنگ: `/api/products/?colors=1,2`
- فعال بودن: `/api/products/?is_active=true`
- موجودی: `/api/products/?in_stock=true`
- محدوده قیمت: `/api/products/?price_range_min=1000&price_range_max=5000`
- دارای تخفیف: `/api/products/?has_discount=true`
- دارای گارانتی: `/api/products/?has_warranty=true`
- گارانتی: `/api/products/?warranties=1,2`
- گروه مشخصات: `/api/products/?spec_groups=1,2`
- فیلتر مشخصات فنی: `/api/products/?specification=RAM:8GB` یا `/api/products/?specification=Storage:128:512`

#### دسته‌بندی (Category)

- جستجو: `/api/categories/?search=کلمه`
- والد: `/api/categories/?parent=1`
- برند: `/api/categories/?brands=1,2`
- دارای محصول: `/api/categories/?has_products=true`
- دارای مشخصات: `/api/categories/?has_specifications=true`
- نام مشخصه: `/api/categories/?spec_name=RAM`
- نوع داده مشخصه: `/api/categories/?spec_data_type=int`
- گروه مشخصات: `/api/categories/?spec_group=1,2`
- فیلتر مشخصات فنی با مقدار: `/api/categories/?spec_value=RAM:8`

#### ویژگی محصول (ProductOption)

- جستجو: `/api/product-options/?search=کلمه`
- محصول: `/api/product-options/?product=1`
- رنگ: `/api/product-options/?color=1`
- گارانتی: `/api/product-options/?warranty=1`
- فعال بودن: `/api/product-options/?is_active=true`
- محدوده قیمت: `/api/product-options/?price_range_min=1000&price_range_max=5000`
- محدوده تخفیف: `/api/product-options/?discount_range_min=10&discount_range_max=50`
- دارای گارانتی: `/api/product-options/?has_warranty=true`
- دارای تخفیف: `/api/product-options/?has_discount=true`

#### گارانتی (Warranty)

- جستجو: `/api/warranties/?search=کلمه`
- نام شرکت: `/api/warranties/?company=شرکت`
- فعال بودن: `/api/warranties/?is_active=true`
- محدوده مدت: `/api/warranties/?duration_range_min=12&duration_range_max=36`
- نیاز به ثبت: `/api/warranties/?registration_required=true`
- دارای محصول: `/api/warranties/?has_product_options=true`

#### گروه مشخصات (SpecificationGroup)

- جستجو: `/api/specification-groups/?search=کلمه`
- دارای مشخصات: `/api/specification-groups/?has_specifications=true`

#### مشخصات فنی (Specification)

- جستجو: `/api/specifications/?search=کلمه`
- دسته‌بندی: `/api/specifications/?categories=1,2`
- گروه: `/api/specifications/?group=1`
- نوع داده: `/api/specifications/?data_type=int`
- نام: `/api/specifications/?name=RAM`
- اصلی بودن: `/api/specifications/?is_main=true`

---

### نکات مهم
- برای فیلترهای چندتایی (مثل categories, brands, tags) مقدارها را با کاما جدا کنید: `?categories=1,2,3`
- برای فیلترهای محدوده‌ای (مثل price_range) از دو پارامتر min و max استفاده کنید: `?price_range_min=1000&price_range_max=5000`
- برای فیلتر مشخصات فنی (specification) فرمت `نام:مقدار` یا `نام:حداقل:حداکثر` را رعایت کنید.
- همه فیلترها را می‌توانید همزمان ترکیب کنید. 