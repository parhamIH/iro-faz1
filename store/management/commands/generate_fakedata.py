from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from store.models import (
    Category, Brand, Product, Specification, ProductSpecification,
    ProductOption, Warranty, Tag, Color, Gallery
)
from django.db import transaction
import random
from decimal import Decimal
from django.core.files.base import ContentFile
from PIL import Image
import io

class Command(BaseCommand):
    help = 'Generate realistic fake data for the store app (clears old data first)'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        fake = Faker('fa_IR')
        self.stdout.write('Clearing old data...')
        # پاک‌سازی داده‌های قبلی
        Gallery.objects.all().delete()
        ProductSpecification.objects.all().delete()
        ProductOption.objects.all().delete()
        Product.objects.all().delete()
        Specification.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        Warranty.objects.all().delete()
        Tag.objects.all().delete()
        Color.objects.all().delete()

        self.stdout.write('Generating new data...')

        # رنگ‌ها
        color_data = [
            ("سفید", "#FFFFFF"),
            ("مشکی", "#000000"),
            ("نقره‌ای", "#C0C0C0"),
            ("آبی", "#0000FF"),
            ("قرمز", "#FF0000"),
            ("خاکستری", "#808080"),
            ("طلایی", "#FFD700"),
        ]
        colors = [Color.objects.create(name=n, hex_code=h) for n, h in color_data]

        # گارانتی‌ها
        warranties = [
            Warranty.objects.create(name="گارانتی ۱۲ ماهه", company="شرکت گارانتی ایران", duration=12),
            Warranty.objects.create(name="گارانتی ۲۴ ماهه", company="شرکت گارانتی پارس", duration=24),
        ]

        # برندها
        brands = {
            'اپل': Brand.objects.create(name='اپل', description='Apple Inc.'),
            'سامسونگ': Brand.objects.create(name='سامسونگ', description='Samsung Electronics'),
            'شیائومی': Brand.objects.create(name='شیائومی', description='Xiaomi'),
            'هواوی': Brand.objects.create(name='هواوی', description='Huawei'),
            'تویوتا': Brand.objects.create(name='تویوتا', description='Toyota'),
            'هیوندای': Brand.objects.create(name='هیوندای', description='Hyundai'),
            'کیا': Brand.objects.create(name='کیا', description='Kia'),
            'ال‌جی': Brand.objects.create(name='ال‌جی', description='LG'),
            'سونی': Brand.objects.create(name='سونی', description='Sony'),
        }

        # دسته‌بندی‌ها
        categories = {
            'موبایل': Category.objects.create(name='موبایل', description='گوشی‌های هوشمند'),
            'تبلت': Category.objects.create(name='تبلت', description='تبلت‌ها'),
            'لپ‌تاپ': Category.objects.create(name='لپ‌تاپ', description='لپ‌تاپ‌ها'),
            'ماشین': Category.objects.create(name='ماشین', description='خودروها'),
            'لوازم خانه': Category.objects.create(name='لوازم خانه', description='لوازم خانگی'),
            'هدفون': Category.objects.create(name='هدفون', description='هدفون و هدست'),
        }

        # مشخصات هر دسته‌بندی
        specs_by_category = {
            'موبایل': [
                ('حافظه داخلی', 'int', 'GB'),
                ('RAM', 'int', 'GB'),
                ('اندازه صفحه', 'decimal', 'اینچ'),
                ('دوربین اصلی', 'int', 'MP'),
                ('باتری', 'int', 'mAh'),
            ],
            'تبلت': [
                ('حافظه داخلی', 'int', 'GB'),
                ('RAM', 'int', 'GB'),
                ('اندازه صفحه', 'decimal', 'اینچ'),
                ('باتری', 'int', 'mAh'),
                ('وزن', 'decimal', 'گرم'),
            ],
            'لپ‌تاپ': [
                ('پردازنده', 'str', None),
                ('حافظه داخلی', 'int', 'GB'),
                ('RAM', 'int', 'GB'),
                ('اندازه صفحه', 'decimal', 'اینچ'),
                ('وزن', 'decimal', 'کیلوگرم'),
            ],
            'ماشین': [
                ('حجم موتور', 'int', 'cc'),
                ('قدرت موتور', 'int', 'hp'),
                ('مصرف سوخت', 'decimal', 'L/100km'),
                ('گیربکس', 'str', None),
                ('تعداد سرنشین', 'int', 'نفر'),
            ],
            'لوازم خانه': [
                ('ظرفیت', 'int', 'لیتر'),
                ('مصرف انرژی', 'str', None),
                ('وزن', 'decimal', 'کیلوگرم'),
                ('رنگ', 'str', None),
                ('نوع', 'str', None),
            ],
            'هدفون': [
                ('نوع اتصال', 'str', None),
                ('عمر باتری', 'int', 'ساعت'),
                ('وزن', 'decimal', 'گرم'),
                ('میکروفون', 'bool', None),
                ('مقاومت در برابر آب', 'bool', None),
            ],
        }

        # ایجاد مشخصات
        spec_objs = {}
        for cat_name, spec_list in specs_by_category.items():
            spec_objs[cat_name] = []
            for name, dtype, unit in spec_list:
                spec = Specification.objects.create(
                    category=categories[cat_name],
                    name=name,
                    data_type=dtype,
                    unit=unit,
                    is_main=True if name in ['حافظه داخلی', 'حجم موتور', 'ظرفیت', 'نوع اتصال'] else False
                )
                spec_objs[cat_name].append(spec)

        # محصولات واقعی برای هر دسته‌بندی
        products_data = {
            'موبایل': [
                {
                    'title': 'iPhone 15 Pro',
                    'brand': brands['اپل'],
                    'specs': [256, 8, Decimal('6.1'), 48, 3274],
                },
                {
                    'title': 'Samsung Galaxy S24 Ultra',
                    'brand': brands['سامسونگ'],
                    'specs': [512, 12, Decimal('6.8'), 200, 5000],
                },
                {
                    'title': 'Xiaomi 13 Pro',
                    'brand': brands['شیائومی'],
                    'specs': [256, 12, Decimal('6.73'), 50, 4820],
                },
            ],
            'تبلت': [
                {
                    'title': 'iPad Pro 12.9',
                    'brand': brands['اپل'],
                    'specs': [512, 8, Decimal('12.9'), 10758, Decimal('682')],
                },
                {
                    'title': 'Samsung Galaxy Tab S9 Ultra',
                    'brand': brands['سامسونگ'],
                    'specs': [256, 12, Decimal('14.6'), 11200, Decimal('732')],
                },
                {
                    'title': 'Xiaomi Pad 6',
                    'brand': brands['شیائومی'],
                    'specs': [128, 8, Decimal('11.0'), 8840, Decimal('490')],
                },
            ],
            'لپ‌تاپ': [
                {
                    'title': 'MacBook Air M2',
                    'brand': brands['اپل'],
                    'specs': ['Apple M2', 512, 8, Decimal('13.6'), Decimal('1.24')],
                },
                {
                    'title': 'Samsung Galaxy Book3 Pro',
                    'brand': brands['سامسونگ'],
                    'specs': ['Intel i7', 1024, 16, Decimal('16.0'), Decimal('1.56')],
                },
                {
                    'title': 'Huawei MateBook X Pro',
                    'brand': brands['هواوی'],
                    'specs': ['Intel i7', 1024, 16, Decimal('14.2'), Decimal('1.26')],
                },
            ],
            'ماشین': [
                {
                    'title': 'تویوتا کرولا 2023',
                    'brand': brands['تویوتا'],
                    'specs': [1800, 140, Decimal('6.5'), 'اتومات', 5],
                },
                {
                    'title': 'هیوندای النترا 2023',
                    'brand': brands['هیوندای'],
                    'specs': [1600, 128, Decimal('7.0'), 'اتومات', 5],
                },
                {
                    'title': 'کیا سراتو 2023',
                    'brand': brands['کیا'],
                    'specs': [2000, 150, Decimal('6.8'), 'اتومات', 5],
                },
            ],
            'لوازم خانه': [
                {
                    'title': 'یخچال سامسونگ RT89',
                    'brand': brands['سامسونگ'],
                    'specs': [700, 'A++', Decimal('120'), 'نقره‌ای', 'یخچال'],
                },
                {
                    'title': 'ماشین لباسشویی ال‌جی WM-1015',
                    'brand': brands['ال‌جی'],
                    'specs': [10, 'A++', Decimal('70'), 'سفید', 'لباسشویی'],
                },
                {
                    'title': 'تلویزیون سونی X90J',
                    'brand': brands['سونی'],
                    'specs': [65, 'A+', Decimal('25'), 'مشکی', 'تلویزیون'],
                },
            ],
            'هدفون': [
                {
                    'title': 'Sony WH-1000XM5',
                    'brand': brands['سونی'],
                    'specs': ['بی‌سیم', 30, Decimal('250'), True, True],
                },
                {
                    'title': 'Apple AirPods Pro 2',
                    'brand': brands['اپل'],
                    'specs': ['بی‌سیم', 6, Decimal('50'), True, True],
                },
                {
                    'title': 'Samsung Galaxy Buds2 Pro',
                    'brand': brands['سامسونگ'],
                    'specs': ['بی‌سیم', 8, Decimal('43'), True, True],
                },
            ],
        }

        # ایجاد محصولات و ویژگی‌ها و آپشن‌ها
        for cat_name, plist in products_data.items():
            category = categories[cat_name]
            specs = spec_objs[cat_name]
            for pdata in plist:
                product = Product.objects.create(
                    title=pdata['title'],
                    brand=pdata['brand'],
                    description=fake.text(),
                    is_active=True
                )
                product.categories.add(category)
                # ویژگی‌ها
                for spec, value in zip(specs, pdata['specs']):
                    ProductSpecification.objects.create(
                        product=product,
                        specification=spec,
                        int_value=value if spec.data_type == 'int' else None,
                        decimal_value=value if spec.data_type == 'decimal' else None,
                        str_value=value if spec.data_type == 'str' else None,
                        bool_value=value if spec.data_type == 'bool' else None,
                        is_main=spec.is_main
                    )
                # آپشن (رنگ و قیمت و گارانتی)
                for color in random.sample(colors, 2):
                    ProductOption.objects.create(
                        product=product,
                        color=color,
                        option_price=random.randint(10_000_000, 100_000_000),
                        quantity=random.randint(1, 20),
                        warranty=random.choice(warranties),
                        is_active=True,
                        is_active_discount=random.choice([True, False]),
                        discount=random.choice([0, 5, 10, 15, 20])
                    )

        # تگ‌ها
        tag_names = ['جدید', 'پرفروش', 'تخفیف‌دار', 'گارانتی دار', 'اصل', 'اورجینال']
        tags = [Tag.objects.create(name=name) for name in tag_names]
        for product in Product.objects.all():
            product.tags.add(*random.sample(tags, random.randint(1, 3)))

        self.stdout.write(self.style.SUCCESS('Successfully generated realistic fake data!')) 