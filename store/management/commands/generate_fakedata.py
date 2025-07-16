from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from store.models import (
    Category, Brand, Product, Specification, ProductSpecification,
    ProductOption, Warranty, Tag, Color, Gallery, SpecificationGroup
)
from django.db import transaction
import random
from decimal import Decimal

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
        SpecificationGroup.objects.all().delete()

        self.stdout.write('Generating new data...')

        # گروه‌های مشخصات
        spec_groups = {
            'مشخصات فنی': SpecificationGroup.objects.create(name='مشخصات فنی'),
            'مشخصات ظاهری': SpecificationGroup.objects.create(name='مشخصات ظاهری'),
            'مشخصات عملکرد': SpecificationGroup.objects.create(name='مشخصات عملکرد'),
            'مشخصات امنیتی': SpecificationGroup.objects.create(name='مشخصات امنیتی'),
        }

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

        # دسته‌بندی‌های والد
        digital_parent = Category.objects.create(name='کالای دیجیتال', description='انواع محصولات دیجیتال')
        vehicle_parent = Category.objects.create(name='وسایل نقلیه', description='انواع وسایل نقلیه')

        # دسته‌بندی‌ها با والد
        categories = {
            'موبایل': Category.objects.create(name='موبایل', description='گوشی‌های هوشمند', parent=digital_parent),
            'تبلت': Category.objects.create(name='تبلت', description='تبلت‌ها', parent=digital_parent),
            'لپ‌تاپ': Category.objects.create(name='لپ‌تاپ', description='لپ‌تاپ‌ها', parent=digital_parent),
            'ماشین': Category.objects.create(name='ماشین', description='خودروها', parent=vehicle_parent),
            'لوازم خانه': Category.objects.create(name='لوازم خانه', description='لوازم خانگی'),
            'هدفون': Category.objects.create(name='هدفون', description='هدفون و هدست'),
        }
        # دسته‌بندی فرزند برای موبایل
        categories['قاب موبایل'] = Category.objects.create(name='قاب موبایل', description='انواع قاب و کاور برای موبایل', parent=categories['موبایل'])

        # اضافه کردن برندها به دسته‌بندی‌ها
        digital_brands = [brands['اپل'], brands['سامسونگ'], brands['شیائومی'], brands['هواوی'], brands['ال‌جی'], brands['سونی']]
        vehicle_brands = [brands['تویوتا'], brands['هیوندای'], brands['کیا']]
        
        for category in [categories['موبایل'], categories['تبلت'], categories['لپ‌تاپ'], categories['هدفون']]:
            category.brand.add(*digital_brands)
        
        for category in [categories['ماشین']]:
            category.brand.add(*vehicle_brands)
        
        categories['لوازم خانه'].brand.add(brands['سامسونگ'], brands['ال‌جی'])
        categories['قاب موبایل'].brand.add(brands['اپل'], brands['سامسونگ'])

        # مشخصات هر دسته‌بندی با گروه‌بندی
        specs_by_category = {
            'موبایل': [
                ('حافظه داخلی', 'int', 'GB', 'مشخصات فنی'),
                ('RAM', 'int', 'GB', 'مشخصات فنی'),
                ('اندازه صفحه', 'decimal', 'اینچ', 'مشخصات ظاهری'),
                ('دوربین اصلی', 'int', 'MP', 'مشخصات عملکرد'),
                ('باتری', 'int', 'mAh', 'مشخصات عملکرد'),
                ('مقاومت در برابر آب', 'bool', None, 'مشخصات امنیتی'),
            ],
            'تبلت': [
                ('حافظه داخلی', 'int', 'GB', 'مشخصات فنی'),
                ('RAM', 'int', 'GB', 'مشخصات فنی'),
                ('اندازه صفحه', 'decimal', 'اینچ', 'مشخصات ظاهری'),
                ('باتری', 'int', 'mAh', 'مشخصات عملکرد'),
                ('وزن', 'decimal', 'گرم', 'مشخصات ظاهری'),
            ],
            'لپ‌تاپ': [
                ('پردازنده', 'str', None, 'مشخصات فنی'),
                ('حافظه داخلی', 'int', 'GB', 'مشخصات فنی'),
                ('RAM', 'int', 'GB', 'مشخصات فنی'),
                ('اندازه صفحه', 'decimal', 'اینچ', 'مشخصات ظاهری'),
                ('وزن', 'decimal', 'کیلوگرم', 'مشخصات ظاهری'),
            ],
            'ماشین': [
                ('حجم موتور', 'int', 'cc', 'مشخصات فنی'),
                ('قدرت موتور', 'int', 'hp', 'مشخصات عملکرد'),
                ('مصرف سوخت', 'decimal', 'L/100km', 'مشخصات عملکرد'),
                ('گیربکس', 'str', None, 'مشخصات فنی'),
                ('تعداد سرنشین', 'int', 'نفر', 'مشخصات ظاهری'),
            ],
            'لوازم خانه': [
                ('ظرفیت', 'int', 'لیتر', 'مشخصات فنی'),
                ('مصرف انرژی', 'str', None, 'مشخصات عملکرد'),
                ('وزن', 'decimal', 'کیلوگرم', 'مشخصات ظاهری'),
                ('رنگ', 'str', None, 'مشخصات ظاهری'),
                ('نوع', 'str', None, 'مشخصات فنی'),
            ],
            'هدفون': [
                ('نوع اتصال', 'str', None, 'مشخصات فنی'),
                ('عمر باتری', 'int', 'ساعت', 'مشخصات عملکرد'),
                ('وزن', 'decimal', 'گرم', 'مشخصات ظاهری'),
                ('میکروفون', 'bool', None, 'مشخصات عملکرد'),
                ('مقاومت در برابر آب', 'bool', None, 'مشخصات امنیتی'),
            ],
            'قاب موبایل': [
                ('جنس', 'str', None, 'مشخصات ظاهری'),
                ('رنگ', 'str', None, 'مشخصات ظاهری'),
                ('ضد ضربه', 'bool', None, 'مشخصات امنیتی'),
                ('مناسب برای مدل', 'str', None, 'مشخصات فنی'),
            ],
        }

        # ایجاد مشخصات
        spec_objs = {}
        for cat_name, spec_list in specs_by_category.items():
            spec_objs[cat_name] = []
            for name, dtype, unit, group_name in spec_list:
                spec = Specification.objects.create(
                    name=name,
                    data_type=dtype,
                    unit=unit,
                    group=spec_groups[group_name],
                    is_main=True if name in ['حافظه داخلی', 'حجم موتور', 'ظرفیت', 'نوع اتصال', 'جنس'] else False
                )
                spec.categories.add(categories[cat_name])
                spec_objs[cat_name].append(spec)

        # محصولات واقعی برای هر دسته‌بندی
        products_data = {
            'موبایل': [
                {
                    'title': 'iPhone 15 Pro',
                    'brand': brands['اپل'],
                    'specs': [256, 8, Decimal('6.1'), 48, 3274, True],
                },
                {
                    'title': 'Samsung Galaxy S24 Ultra',
                    'brand': brands['سامسونگ'],
                    'specs': [512, 12, Decimal('6.8'), 200, 5000, True],
                },
            ],
            'قاب موبایل': [
                {
                    'title': 'قاب سیلیکونی آیفون 15',
                    'brand': brands['اپل'],
                    'specs': ['سیلیکون', 'قرمز', True, 'iPhone 15'],
                },
                {
                    'title': 'قاب ضدضربه سامسونگ S24',
                    'brand': brands['سامسونگ'],
                    'specs': ['پلاستیک سخت', 'مشکی', True, 'Galaxy S24'],
                },
            ],
            'تبلت': [
                {
                    'title': 'iPad Pro 12.9',
                    'brand': brands['اپل'],
                    'specs': [512, 8, Decimal('12.9'), 10758, Decimal('682')],
                },
            ],
            'لپ‌تاپ': [
                {
                    'title': 'MacBook Air M2',
                    'brand': brands['اپل'],
                    'specs': ['Apple M2', 512, 8, Decimal('13.6'), Decimal('1.24')],
                },
            ],
            'ماشین': [
                {
                    'title': 'تویوتا کرولا 2023',
                    'brand': brands['تویوتا'],
                    'specs': [1800, 140, Decimal('6.5'), 'اتومات', 5],
                },
            ],
            'لوازم خانه': [
                {
                    'title': 'یخچال سامسونگ RT89',
                    'brand': brands['سامسونگ'],
                    'specs': [700, 'A++', Decimal('120'), 'نقره‌ای', 'یخچال'],
                },
            ],
            'هدفون': [
                {
                    'title': 'Sony WH-1000XM5',
                    'brand': brands['سونی'],
                    'specs': ['بی‌سیم', 30, Decimal('250'), True, True],
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
                        specification_value=str(value),
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

        # گالری تصاویر
        for product_option in ProductOption.objects.all():
            for i in range(random.randint(1, 3)):
                Gallery.objects.create(
                    product=product_option,
                    image=None,  # در محیط واقعی فایل تصویر اضافه کنید
                    alt_text=f"تصویر {i+1} برای {product_option.product.title}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated:\n'
                f'- {len(colors)} colors\n'
                f'- {len(warranties)} warranties\n'
                f'- {len(brands)} brands\n'
                f'- {len(categories)} categories\n'
                f'- {len(spec_groups)} specification groups\n'
                f'- {Specification.objects.count()} specifications\n'
                f'- {Product.objects.count()} products\n'
                f'- {ProductOption.objects.count()} product options\n'
                f'- {ProductSpecification.objects.count()} product specifications\n'
                f'- {len(tags)} tags\n'
                f'- {Gallery.objects.count()} gallery images'
            )
        ) 