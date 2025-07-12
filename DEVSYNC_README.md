# Django DevSync - راهنمای استفاده

## 🚀 Django DevSync چیست؟

`django-devsync` یک ابزار قدرتمند برای توسعه Django است که به طور خودکار تغییرات فایل‌ها را تشخیص داده و سرور را reload می‌کند.

## ✨ ویژگی‌ها

- 🔄 **Auto-reload**: تشخیص خودکار تغییرات فایل‌ها
- 📁 **Smart Watching**: نظارت بر پوشه‌های خاص
- 🚫 **Ignore Patterns**: نادیده گرفتن فایل‌های غیرضروری
- ⚡ **Fast Reload**: reload سریع و بهینه
- 🔔 **Notifications**: اعلان‌های تغییرات

## 🛠️ نصب و راه‌اندازی

### 1. نصب پکیج
```bash
pip install django-devsync
```

### 2. اضافه کردن به INSTALLED_APPS
```python
INSTALLED_APPS = [
    # ...
    'devsync',
    # ...
]
```

### 3. تنظیمات در settings.py
```python
if DEBUG:
    DEVSYNC = {
        'ENABLED': True,
        'WATCH_DIRS': [
            'excel_file_handling',
            'store',
            'accounts',
            'cart',
            'installments',
        ],
        'IGNORE_PATTERNS': [
            '*.pyc',
            '__pycache__',
            '*.log',
            '.git',
            'media',
            'static',
        ],
        'RELOAD_DELAY': 1.0,
    }
```

## 🎯 نحوه استفاده

### روش 1: اجرای مستقیم
```bash
python manage.py runserver
```

### روش 2: استفاده از اسکریپت
```bash
python run_dev.py
```

### روش 3: با تنظیمات پیشرفته
```bash
python manage.py runserver --settings=config.settings
```

## 📁 فایل‌های پیکربندی

### devsync.json
```json
{
  "enabled": true,
  "watch_dirs": [
    "excel_file_handling",
    "store",
    "accounts",
    "cart",
    "installments"
  ],
  "ignore_patterns": [
    "*.pyc",
    "__pycache__",
    "*.log",
    ".git",
    "media",
    "static"
  ],
  "reload_delay": 1.0,
  "auto_reload": true,
  "notifications": true,
  "log_level": "INFO"
}
```

## 🔧 تنظیمات پیشرفته

### تغییر فایل‌های تحت نظارت
```python
DEVSYNC = {
    'WATCH_DIRS': [
        'your_app_name',
        'another_app',
    ],
}
```

### تنظیم الگوهای نادیده گرفته شده
```python
DEVSYNC = {
    'IGNORE_PATTERNS': [
        '*.pyc',
        '__pycache__',
        '*.log',
        '.git',
        'media',
        'static',
        'venv',
        'node_modules',
    ],
}
```

### تنظیم تاخیر reload
```python
DEVSYNC = {
    'RELOAD_DELAY': 0.5,  # 0.5 ثانیه
}
```

## 🚨 نکات مهم

1. **فقط در محیط توسعه**: DevSync فقط در `DEBUG=True` فعال می‌شود
2. **عملکرد**: در فایل‌های بزرگ ممکن است کمی کند باشد
3. **مصرف منابع**: CPU بیشتری مصرف می‌کند
4. **امنیت**: در production غیرفعال است

## 🔍 عیب‌یابی

### مشکل: DevSync کار نمی‌کند
```bash
# بررسی نصب
pip list | grep devsync

# بررسی تنظیمات
python manage.py check
```

### مشکل: Reload کند است
```python
# کاهش تاخیر
'RELOAD_DELAY': 0.5,
```

### مشکل: فایل‌های اضافی reload می‌شوند
```python
# اضافه کردن الگوهای ignore
'IGNORE_PATTERNS': [
    '*.pyc',
    '__pycache__',
    '*.log',
    '.git',
    'media',
    'static',
    'venv',
    'node_modules',
    '*.swp',
    '*.swo',
    '.DS_Store'
],
```

## 📚 منابع بیشتر

- [Django DevSync Documentation](https://github.com/your-repo/django-devsync)
- [Django Development Best Practices](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Python File Watching](https://docs.python.org/3/library/watchdog.html)

## 🤝 مشارکت

برای گزارش مشکلات یا پیشنهادات، لطفاً issue ایجاد کنید.

---

**نکته**: این ابزار فقط برای محیط توسعه توصیه می‌شود و نباید در production استفاده شود. 