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