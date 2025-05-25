from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from store.models import (
    Brand, Category, Product,
    Color, ProductOption, Gallery,
    Specification, ProductSpecification
)
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populates the database with sample store data'

    def handle(self, *args, **options):
        # Clear existing data
        Gallery.objects.all().delete()
        ProductOption.objects.all().delete()
        ProductSpecification.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        Color.objects.all().delete()
        Specification.objects.all().delete()

        self.stdout.write('Starting to populate data...')
        
        # 1. Create Brands with proper categorization
        digital_brands = [
            {"name": "سامسونگ", "description": "برند معتبر در زمینه موبایل، لپ‌تاپ و لوازم دیجیتال"},
            {"name": "اپل", "description": "تولید کننده محصولات با کیفیت دیجیتال"},
            {"name": "ایسوس", "description": "متخصص در تولید لپ‌تاپ و قطعات کامپیوتر"},
            {"name": "شیائومی", "description": "تولید کننده محصولات دیجیتال با قیمت مناسب"},
        ]
        
        home_brands = [
            {"name": "ال جی", "description": "تولید کننده لوازم خانگی با کیفیت"},
            {"name": "بوش", "description": "برند آلمانی لوازم خانگی"},
            {"name": "اسنوا", "description": "تولید کننده ایرانی لوازم خانگی"},
            {"name": "سامسونگ هوم", "description": "بخش لوازم خانگی سامسونگ"},
        ]
        
        brands = []
        for brand_data in digital_brands + home_brands:
            brand, _ = Brand.objects.get_or_create(**brand_data)
            brands.append(brand)
        self.stdout.write(f'{len(brands)} brands created.')

        # 2. Create Colors
        colors_data = [
            {"name": "سفید", "hex_code": "#FFFFFF"},
            {"name": "مشکی", "hex_code": "#000000"},
            {"name": "نقره‌ای", "hex_code": "#C0C0C0"},
            {"name": "خاکستری", "hex_code": "#808080"},
            {"name": "طلایی", "hex_code": "#FFD700"},
            {"name": "آبی", "hex_code": "#0000FF"},
            {"name": "قرمز", "hex_code": "#FF0000"},
        ]
        colors = []
        for c_data in colors_data:
            color, _ = Color.objects.get_or_create(hex_code=c_data['hex_code'], defaults=c_data)
            colors.append(color)
        self.stdout.write(f'{len(colors)} colors created.')

        # 3. Create Categories with proper hierarchy
        # دسته‌بندی کالای دیجیتال
        digital = Category.objects.create(
            name="کالای دیجیتال",
            description="انواع محصولات دیجیتال شامل موبایل، لپ‌تاپ و لوازم جانبی"
        )
        
        digital_cats = [
            {"name": "موبایل", "description": "گوشی‌های هوشمند"},
            {"name": "لپ‌تاپ", "description": "لپ‌تاپ و نوت‌بوک"},
            {"name": "تبلت", "description": "تبلت و کتابخوان"},
            {"name": "لوازم جانبی موبایل", "description": "قاب، محافظ صفحه و شارژر"},
        ]
        
        # دسته‌بندی لوازم خانگی
        home = Category.objects.create(
            name="لوازم خانگی",
            description="انواع لوازم برقی خانگی"
        )
        
        home_cats = [
            {"name": "یخچال و فریزر", "description": "یخچال، فریزر و ساید بای ساید"},
            {"name": "ماشین لباسشویی", "description": "ماشین لباسشویی اتوماتیک"},
            {"name": "اجاق گاز", "description": "اجاق گاز فردار و رومیزی"},
            {"name": "ماشین ظرفشویی", "description": "ماشین ظرفشویی مبله و توکار"},
        ]

        categories = []
        # ایجاد زیر دسته‌های دیجیتال
        for cat in digital_cats:
            category = Category.objects.create(parent=digital, **cat)
            categories.append(category)
            
        # ایجاد زیر دسته‌های لوازم خانگی
        for cat in home_cats:
            category = Category.objects.create(parent=home, **cat)
            categories.append(category)
            
        categories.extend([digital, home])
        self.stdout.write(f'{len(categories)} categories created.')

        # Create specifications
        self.stdout.write('Creating specifications...')
        
        # Common specifications for all categories
        common_specs = {
            "color": {
                "name": "رنگ",
                "data_type": "str",
                "unit": None
            },
            "warranty": {
                "name": "گارانتی",
                "data_type": "str",
                "unit": "ماه"
            }
        }

        # Mobile specifications
        mobile_specs = {
            "battery": {
                "name": "حجم باتری",
                "data_type": "int",
                "unit": "mAh"
            },
            "screen_size": {
                "name": "اندازه صفحه نمایش",
                "data_type": "decimal",
                "unit": "اینچ"
            },
            "screen_tech": {
                "name": "فناوری صفحه‌نمایش",
                "data_type": "str",
                "unit": None
            },
            "dual_sim": {
                "name": "دو سیم‌کارت",
                "data_type": "bool",
                "unit": None
            }
        }

        # Laptop specifications
        laptop_specs = {
            "screen_size": {
                "name": "سایز صفحه نمایش",
                "data_type": "decimal",
                "unit": "اینچ"
            },
            "battery": {
                "name": "ظرفیت باتری",
                "data_type": "int",
                "unit": "Wh"
            },
            "weight": {
                "name": "وزن",
                "data_type": "decimal",
                "unit": "کیلوگرم"
            },
            "touch_screen": {
                "name": "قابلیت لمسی",
                "data_type": "bool",
                "unit": None
            }
        }

        # Refrigerator specifications
        refrigerator_specs = {
            "fridge_volume": {
                "name": "حجم یخچال",
                "data_type": "int",
                "unit": "لیتر"
            },
            "freezer_volume": {
                "name": "حجم فریزر",
                "data_type": "int",
                "unit": "لیتر"
            },
            "energy_usage": {
                "name": "مصرف سالانه انرژی",
                "data_type": "int",
                "unit": "کیلووات ساعت"
            },
            "water_dispenser": {
                "name": "قابلیت آبریز",
                "data_type": "bool",
                "unit": None
            }
        }

        # Washing machine specifications
        washing_specs = {
            "spin_speed": {
                "name": "سرعت حداکثر چرخش",
                "data_type": "int",
                "unit": "دور بر دقیقه"
            },
            "water_usage": {
                "name": "مصرف آب",
                "data_type": "decimal",
                "unit": "لیتر"
            },
            "add_wash": {
                "name": "قابلیت اضافه کردن لباس حین شستشو",
                "data_type": "bool",
                "unit": None
            }
        }

        # Create specifications for each category
        specs_mapping = {
            "موبایل": mobile_specs,
            "لپ‌تاپ": laptop_specs,
            "یخچال و فریزر": refrigerator_specs,
            "ماشین لباسشویی": washing_specs,
        }

        specifications = {}
        # Add common specs to all categories
        for category_name, specs_list in specs_mapping.items():
            category = Category.objects.get(name=category_name)
            
            # Add common specifications
            for spec_name, spec_data in common_specs.items():
                spec = Specification.objects.create(
                    category=category,
                    **spec_data
                )
                specifications[f"{category_name}_{spec_name}"] = spec
            
            # Add category-specific specifications
            for spec_name, spec_data in specs_list.items():
                spec = Specification.objects.create(
                    category=category,
                    **spec_data
                )
                specifications[f"{category_name}_{spec_name}"] = spec

        self.stdout.write(f'{len(specifications)} specifications created.')

        # Create products with their specifications
        self.stdout.write('Creating products...')
        
        products_data = [
            {
                "title": "گوشی موبایل سامسونگ مدل Galaxy S23 Ultra",
                "description": "پرچمدار سامسونگ با دوربین 200 مگاپیکسلی",
                "brand": Brand.objects.get(name="سامسونگ"),
                "category": Category.objects.get(name="موبایل"),
                "colors": ["مشکی", "نقره‌ای", "طلایی"],
                "base_price": 45000000,
                "has_discount": True,
                "discount_percentage": 10,
                "specifications": {
                    "battery": {"int_value": 5000},
                    "screen_size": {"decimal_value": Decimal("6.8")},
                    "screen_tech": {"str_value": "Dynamic AMOLED 2X"},
                    "dual_sim": {"bool_value": True},
                    "color": {"str_value": "Phantom Black"},
                    "warranty": {"str_value": "18 ماه"}
                }
            },
            {
                "title": "لپ تاپ ایسوس مدل ROG Strix G15",
                "description": "لپ تاپ گیمینگ با پردازنده قدرتمند",
                "brand": Brand.objects.get(name="ایسوس"),
                "category": Category.objects.get(name="لپ‌تاپ"),
                "colors": ["مشکی", "خاکستری"],
                "base_price": 52000000,
                "has_discount": False,
                "specifications": {
                    "screen_size": {"decimal_value": Decimal("15.6")},
                    "battery": {"int_value": 90},
                    "weight": {"decimal_value": Decimal("2.3")},
                    "touch_screen": {"bool_value": False},
                    "color": {"str_value": "مشکی"},
                    "warranty": {"str_value": "24 ماه"}
                }
            },
            {
                "title": "یخچال و فریزر ساید بای ساید ال جی",
                "description": "یخچال و فریزر ساید بای ساید با تکنولوژی اینورتر",
                "brand": Brand.objects.get(name="ال جی"),
                "category": Category.objects.get(name="یخچال و فریزر"),
                "colors": ["نقره‌ای", "سفید"],
                "base_price": 85000000,
                "has_discount": True,
                "discount_percentage": 15,
                "specifications": {
                    "fridge_volume": {"int_value": 380},
                    "freezer_volume": {"int_value": 220},
                    "energy_usage": {"int_value": 420},
                    "water_dispenser": {"bool_value": True},
                    "color": {"str_value": "نقره‌ای"},
                    "warranty": {"str_value": "24 ماه"}
                }
            },
            {
                "title": "ماشین لباسشویی اسنوا مدل SWM-84518",
                "description": "ماشین لباسشویی 8 کیلویی اسنوا",
                "brand": Brand.objects.get(name="اسنوا"),
                "category": Category.objects.get(name="ماشین لباسشویی"),
                "colors": ["سفید"],
                "base_price": 32000000,
                "has_discount": True,
                "discount_percentage": 5,
                "specifications": {
                    "spin_speed": {"int_value": 1400},
                    "water_usage": {"decimal_value": Decimal("52.5")},
                    "add_wash": {"bool_value": True},
                    "color": {"str_value": "سفید"},
                    "warranty": {"str_value": "24 ماه"}
                }
            }
        ]

        products = []
        for product_data in products_data:
            # Create the product
            product = Product.objects.create(
                title=product_data['title'],
                description=product_data['description'],
                brand=product_data['brand']
            )
            product.categories.add(product_data['category'])
            
            # Add specifications
            if 'specifications' in product_data:
                for spec_name, value_data in product_data['specifications'].items():
                    spec = Specification.objects.get(
                        category=product_data['category'],
                        name=specs_mapping.get(product_data['category'].name, {}).get(spec_name, {}).get('name') or
                             common_specs.get(spec_name, {}).get('name')
                    )
                    ProductSpecification.objects.create(
                        product=product,
                        specification=spec,
                        **value_data
                    )
            
            # Create product options for each color
            for color_name in product_data['colors']:
                color = Color.objects.get(name=color_name)
                option = ProductOption.objects.create(
                    product=product,
                    color=color,
                    option_price=product_data['base_price'],
                    quantity=random.randint(5, 20),
                    is_active=True
                )
                
                # Apply discount if specified
                if product_data.get('has_discount', False):
                    discount_percentage = product_data.get('discount_percentage', 0)
                    if discount_percentage > 0:
                        option.is_active_discount = True
                        option.discount = discount_percentage
                        option.discount_start_date = timezone.now()
                        option.discount_end_date = timezone.now() + timedelta(days=30)
                        option.save()

                # Create gallery images for each product option
                for i in range(1, 4):
                    Gallery.objects.create(
                        product=option,
                        image=f'product_gallery/sample_{i}.jpg',
                        alt_text=f'{product.title} - {color_name} - تصویر {i}'
                    )
            
            products.append(product)

        self.stdout.write(f'{len(products)} products created.')
        self.stdout.write(self.style.SUCCESS('Successfully populated store data with realistic information!')) 