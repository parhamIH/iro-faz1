from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from store.models import (
    Category, Brand, Product, Specification, ProductSpecification,
    ProductOption, Warranty, Tag, Color, Gallery
)
from accounts.models import CustomUser, Address, Provider
import random
from decimal import Decimal
from django.core.files.base import ContentFile
from PIL import Image
import io

class Command(BaseCommand):
    help = 'Generate fake data for the store app'

    def handle(self, *args, **kwargs):
        fake = Faker('fa_IR')  # Using Persian locale for more realistic data
        self.stdout.write('Starting to generate fake data...')

        # Create Colors
        colors = [
            ('سیاه', '#000000'),
            ('سفید', '#FFFFFF'),
            ('قرمز', '#FF0000'),
            ('آبی', '#0000FF'),
            ('سبز', '#008000'),
            ('طلایی', '#FFD700'),
            ('نقره‌ای', '#C0C0C0'),
        ]
        color_objects = []
        for name, hex_code in colors:
            color = Color.objects.create(name=name, hex_code=hex_code)
            color_objects.append(color)

        # Create Warranties
        warranties = []
        warranty_data = [
            ('گارانتی 12 ماهه', 'شرکت گارانتی ایران', 12),
            ('گارانتی 24 ماهه', 'شرکت گارانتی پارس', 24),
            ('گارانتی 6 ماهه', 'شرکت گارانتی آریا', 6),
        ]
        for name, company, duration in warranty_data:
            warranty = Warranty.objects.create(
                name=name,
                company=company,
                duration=duration,
                description=fake.text(),
                terms_conditions=fake.text(),
                support_phone=fake.phone_number(),
                registration_required=random.choice([True, False])
            )
            warranties.append(warranty)

        # Create Brands
        brands = []
        brand_data = [
            ('اپل', 'شرکت اپل'),
            ('سامسونگ', 'شرکت سامسونگ'),
            ('شیائومی', 'شرکت شیائومی'),
            ('هواوی', 'شرکت هواوی'),
            ('سونی', 'شرکت سونی'),
        ]
        for name, description in brand_data:
            brand = Brand.objects.create(
                name=name,
                description=description
            )
            brands.append(brand)

        # Create Categories
        categories = []
        category_data = [
            ('موبایل', None),
            ('لپ تاپ', None),
            ('تبلت', None),
            ('هدفون', None),
            ('گوشی‌های اپل', 'موبایل'),
            ('گوشی‌های سامسونگ', 'موبایل'),
            ('لپ تاپ‌های گیمینگ', 'لپ تاپ'),
            ('لپ تاپ‌های اداری', 'لپ تاپ'),
        ]
        
        # First create parent categories
        category_dict = {}
        for name, parent_name in category_data:
            if parent_name is None:
                category = Category.objects.create(
                    name=name,
                    description=fake.text(),
                    brand=random.choice(brands) if random.random() > 0.5 else None
                )
                category_dict[name] = category
                categories.append(category)

        # Then create child categories
        for name, parent_name in category_data:
            if parent_name is not None:
                parent = category_dict.get(parent_name)
                if parent:
                    category = Category.objects.create(
                        name=name,
                        description=fake.text(),
                        parent=parent,
                        brand=random.choice(brands) if random.random() > 0.5 else None
                    )
                    categories.append(category)

        # Create Specifications
        specifications = []
        spec_data = [
            ('حافظه داخلی', 'int', 'GB'),
            ('RAM', 'int', 'GB'),
            ('اندازه صفحه نمایش', 'decimal', 'اینچ'),
            ('دوربین اصلی', 'int', 'مگاپیکسل'),
            ('دوربین سلفی', 'int', 'مگاپیکسل'),
            ('باتری', 'int', 'mAh'),
            ('وزن', 'decimal', 'گرم'),
            ('ضد آب', 'bool', None),
            ('شارژ سریع', 'bool', None),
        ]

        for category in categories:
            for name, data_type, unit in spec_data:
                spec = Specification.objects.create(
                    category=category,
                    name=name,
                    data_type=data_type,
                    unit=unit,
                    is_main=random.choice([True, False])
                )
                specifications.append(spec)

        # Create Products
        products = []
        product_data = [
            ('iPhone 14 Pro', 'اپل', 'گوشی‌های اپل'),
            ('iPhone 13 Pro', 'اپل', 'گوشی‌های اپل'),
            ('Galaxy S23 Ultra', 'سامسونگ', 'گوشی‌های سامسونگ'),
            ('Galaxy S22', 'سامسونگ', 'گوشی‌های سامسونگ'),
            ('Xiaomi 13 Pro', 'شیائومی', 'موبایل'),
            ('Huawei P60 Pro', 'هواوی', 'موبایل'),
        ]

        for title, brand_name, category_name in product_data:
            brand = next((b for b in brands if b.name == brand_name), random.choice(brands))
            category = next((c for c in categories if c.name == category_name), random.choice(categories))
            
            product = Product.objects.create(
                title=title,
                description=fake.text(),
                brand=brand,
                is_active=True
            )
            product.categories.add(category)
            products.append(product)

            # Create Product Specifications
            for spec in specifications:
                if spec.category == category or spec.category.parent == category:
                    value = None
                    if spec.data_type == 'int':
                        value = random.randint(64, 512) if spec.name == 'حافظه داخلی' else random.randint(4, 16)
                    elif spec.data_type == 'decimal':
                        value = Decimal(str(random.uniform(5.0, 7.0))) if spec.name == 'اندازه صفحه نمایش' else Decimal(str(random.uniform(150.0, 250.0)))
                    elif spec.data_type == 'bool':
                        value = random.choice([True, False])
                    elif spec.data_type == 'str':
                        value = fake.word()

                    if value is not None:
                        ProductSpecification.objects.create(
                            product=product,
                            specification=spec,
                            int_value=value if spec.data_type == 'int' else None,
                            decimal_value=value if spec.data_type == 'decimal' else None,
                            str_value=str(value) if spec.data_type == 'str' else None,
                            bool_value=value if spec.data_type == 'bool' else None
                        )

            # Create Product Options
            for color in random.sample(color_objects, random.randint(1, 3)):
                option = ProductOption.objects.create(
                    product=product,
                    color=color,
                    option_price=random.randint(20000000, 50000000),
                    quantity=random.randint(5, 50),
                    warranty=random.choice(warranties),
                    is_active=True
                )

                # Add discount to some options
                if random.random() > 0.7:
                    option.is_active_discount = True
                    option.discount = random.randint(5, 30)
                    option.discount_start_date = timezone.now()
                    option.discount_end_date = timezone.now() + timezone.timedelta(days=random.randint(7, 30))
                    option.save()

        # Create Tags
        tags = []
        tag_names = ['جدید', 'پرفروش', 'تخفیف‌دار', 'گارانتی دار', 'اصل', 'اورجینال']
        for name in tag_names:
            tag = Tag.objects.create(name=name)
            tags.append(tag)

        # Add tags to random products
        for product in products:
            product.tags.add(*random.sample(tags, random.randint(1, 3)))

        self.stdout.write(self.style.SUCCESS('Successfully generated fake data')) 