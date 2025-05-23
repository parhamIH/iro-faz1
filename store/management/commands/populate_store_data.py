from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

from store.models import (
    Category, Product, Feature, 
    ProductOption, Gallery, Color, Brand,
    Specification, ProductSpecification
)

class Command(BaseCommand):
    help = 'Populates the database with realistic store data'

    def handle(self, *args, **options):
        self.stdout.write('Deleting old data...')
        # ترتیب حذف مهم است به دلیل روابط ForeignKey
        Gallery.objects.all().delete()
        ProductOption.objects.all().delete()
        ProductSpecification.objects.all().delete()
        Product.objects.all().delete()
        Feature.objects.all().delete()
        Specification.objects.all().delete()
        Color.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Old data deleted.'))

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

        # 4. Create Features based on category
        mobile_cat = Category.objects.get(name="موبایل")
        laptop_cat = Category.objects.get(name="لپ‌تاپ")
        refrigerator_cat = Category.objects.get(name="یخچال و فریزر")
        washing_cat = Category.objects.get(name="ماشین لباسشویی")

        features = []
        # ویژگی‌های عمومی
        common_features = [
            {"name": "رنگ", "value": "متنوع", "is_main_feature": True},
            {"name": "گارانتی", "value": "18 ماه", "is_main_feature": True},
        ]

        # ویژگی‌های موبایل
        mobile_features = [
            {"name": "حافظه داخلی", "value": "128 گیگابایت", "is_main_feature": True},
            {"name": "رم", "value": "8 گیگابایت", "is_main_feature": True},
            {"name": "پردازنده", "value": "Snapdragon", "is_main_feature": True},
            {"name": "دوربین اصلی", "value": "48 مگاپیکسل", "is_main_feature": True},
        ]

        # ویژگی‌های لپ‌تاپ
        laptop_features = [
            {"name": "پردازنده", "value": "Core i7", "is_main_feature": True},
            {"name": "حافظه RAM", "value": "16 گیگابایت", "is_main_feature": True},
            {"name": "حافظه داخلی", "value": "512 گیگابایت SSD", "is_main_feature": True},
            {"name": "کارت گرافیک", "value": "NVIDIA RTX", "is_main_feature": True},
        ]

        # ویژگی‌های یخچال
        refrigerator_features = [
            {"name": "حجم کل", "value": "500 لیتر", "is_main_feature": True},
            {"name": "نوع یخچال", "value": "ساید بای ساید", "is_main_feature": True},
            {"name": "برچسب انرژی", "value": "A++", "is_main_feature": True},
        ]

        # ویژگی‌های ماشین لباسشویی
        washing_machine_features = [
            {"name": "ظرفیت", "value": "8 کیلوگرم", "is_main_feature": True},
            {"name": "نوع موتور", "value": "دایرکت درایو", "is_main_feature": True},
            {"name": "تعداد برنامه شستشو", "value": "16", "is_main_feature": True},
            {"name": "برچسب انرژی", "value": "A+++", "is_main_feature": True},
        ]

        # ایجاد ویژگی‌ها برای هر دسته
        for feature_data in common_features:
            for category in [mobile_cat, laptop_cat, refrigerator_cat, washing_cat]:
                feature_data = feature_data.copy()
                feature, _ = Feature.objects.get_or_create(
                    name=feature_data['name'],
                    category=category,
                    defaults=feature_data
                )
                features.append(feature)

        # ویژگی‌های اختصاصی موبایل
        for feature_data in mobile_features:
            feature, _ = Feature.objects.get_or_create(
                name=feature_data['name'],
                category=mobile_cat,
                defaults=feature_data
            )
            features.append(feature)

        # ویژگی‌های اختصاصی لپ‌تاپ
        for feature_data in laptop_features:
            feature, _ = Feature.objects.get_or_create(
                name=feature_data['name'],
                category=laptop_cat,
                defaults=feature_data
            )
            features.append(feature)

        # ویژگی‌های اختصاصی یخچال
        for feature_data in refrigerator_features:
            feature, _ = Feature.objects.get_or_create(
                name=feature_data['name'],
                category=refrigerator_cat,
                defaults=feature_data
            )
            features.append(feature)

        # ویژگی‌های اختصاصی ماشین لباسشویی
        for feature_data in washing_machine_features:
            feature, _ = Feature.objects.get_or_create(
                name=feature_data['name'],
                category=washing_cat,
                defaults=feature_data
            )
            features.append(feature)

        self.stdout.write(f'{len(features)} features created.')

        # Add new section for creating specifications
        self.stdout.write('Creating specifications...')
        
        # تعریف مشخصات موبایل
        mobile_specs = [
            {
                "name": "حجم باتری",
                "data_type": "int",
                "unit": "mAh",
            },
            {
                "name": "اندازه صفحه نمایش",
                "data_type": "decimal",
                "unit": "اینچ",
            },
            {
                "name": "فناوری صفحه‌نمایش",
                "data_type": "str",
            },
            {
                "name": "دو سیم‌کارت",
                "data_type": "bool",
            },
        ]

        # تعریف مشخصات لپ‌تاپ
        laptop_specs = [
            {
                "name": "سایز صفحه نمایش",
                "data_type": "decimal",
                "unit": "اینچ",
            },
            {
                "name": "ظرفیت باتری",
                "data_type": "int",
                "unit": "Wh",
            },
            {
                "name": "وزن",
                "data_type": "decimal",
                "unit": "کیلوگرم",
            },
            {
                "name": "قابلیت لمسی",
                "data_type": "bool",
            },
        ]

        # تعریف مشخصات یخچال
        refrigerator_specs = [
            {
                "name": "حجم یخچال",
                "data_type": "int",
                "unit": "لیتر",
            },
            {
                "name": "حجم فریزر",
                "data_type": "int",
                "unit": "لیتر",
            },
            {
                "name": "مصرف سالانه انرژی",
                "data_type": "int",
                "unit": "کیلووات ساعت",
            },
            {
                "name": "قابلیت آبریز",
                "data_type": "bool",
            },
        ]

        # تعریف مشخصات ماشین لباسشویی
        washing_specs = [
            {
                "name": "سرعت حداکثر چرخش",
                "data_type": "int",
                "unit": "دور بر دقیقه",
            },
            {
                "name": "مصرف آب",
                "data_type": "decimal",
                "unit": "لیتر",
            },
            {
                "name": "قابلیت اضافه کردن لباس حین شستشو",
                "data_type": "bool",
            },
        ]

        # ایجاد مشخصات برای هر دسته
        specs_mapping = {
            "موبایل": mobile_specs,
            "لپ‌تاپ": laptop_specs,
            "یخچال و فریزر": refrigerator_specs,
            "ماشین لباسشویی": washing_specs,
        }

        specifications = []
        for category_name, specs_list in specs_mapping.items():
            category = Category.objects.get(name=category_name)
            for spec_data in specs_list:
                spec = Specification.objects.create(
                    category=category,
                    **spec_data
                )
                specifications.append(spec)

        self.stdout.write(f'{len(specifications)} specifications created.')

        # 5. Create Products with realistic data
        products_data = [
            {
                "title": "گوشی موبایل سامسونگ مدل Galaxy S23 Ultra",
                "description": "پرچمدار سامسونگ با دوربین 200 مگاپیکسلی",
                "category": mobile_cat,
                "brand": Brand.objects.get(name="سامسونگ"),
                "features": mobile_features,
                "colors": ["مشکی", "نقره‌ای", "طلایی"],
                "base_price": 45000000,
                "has_discount": True,
                "discount_percentage": 10,
                "specifications": {
                    "حجم باتری": {"int_value": 5000},
                    "اندازه صفحه نمایش": {"decimal_value": 6.8},
                    "فناوری صفحه‌نمایش": {"str_value": "Dynamic AMOLED 2X"},
                    "دو سیم‌کارت": {"bool_value": True},
                }
            },
            {
                "title": "لپ تاپ ایسوس مدل ROG Strix G15",
                "description": "لپ تاپ گیمینگ با پردازنده قدرتمند",
                "category": laptop_cat,
                "brand": Brand.objects.get(name="ایسوس"),
                "features": laptop_features,
                "colors": ["مشکی", "خاکستری"],
                "base_price": 52000000,
                "has_discount": False,
                "specifications": {
                    "سایز صفحه نمایش": {"decimal_value": 15.6},
                    "ظرفیت باتری": {"int_value": 90},
                    "وزن": {"decimal_value": 2.3},
                    "قابلیت لمسی": {"bool_value": False},
                }
            },
            {
                "title": "یخچال و فریزر ساید بای ساید ال جی",
                "description": "یخچال و فریزر ساید بای ساید با تکنولوژی اینورتر",
                "category": refrigerator_cat,
                "brand": Brand.objects.get(name="ال جی"),
                "features": refrigerator_features,
                "colors": ["نقره‌ای", "سفید"],
                "base_price": 85000000,
                "has_discount": True,
                "discount_percentage": 15,
                "specifications": {
                    "حجم یخچال": {"int_value": 380},
                    "حجم فریزر": {"int_value": 220},
                    "مصرف سالانه انرژی": {"int_value": 420},
                    "قابلیت آبریز": {"bool_value": True},
                }
            },
            {
                "title": "ماشین لباسشویی اسنوا مدل SWM-84518",
                "description": "ماشین لباسشویی 8 کیلویی اسنوا",
                "category": washing_cat,
                "brand": Brand.objects.get(name="اسنوا"),
                "features": washing_machine_features,
                "colors": ["سفید"],
                "base_price": 32000000,
                "has_discount": True,
                "discount_percentage": 5,
                "specifications": {
                    "سرعت حداکثر چرخش": {"int_value": 1400},
                    "مصرف آب": {"decimal_value": 52.5},
                    "قابلیت اضافه کردن لباس حین شستشو": {"bool_value": True},
                }
            }
        ]

        products = []
        for product_data in products_data:
            # ایجاد محصول
            product = Product.objects.create(
                title=product_data['title'],
                description=product_data['description'],
                brand=product_data['brand']
            )
            product.categories.add(product_data['category'])
            product.feature.set(Feature.objects.filter(category=product_data['category']))
            
            # اضافه کردن مشخصات محصول
            if 'specifications' in product_data:
                for spec_name, value_data in product_data['specifications'].items():
                    spec = Specification.objects.get(
                        category=product_data['category'],
                        name=spec_name
                    )
                    ProductSpecification.objects.create(
                        product=product,
                        specification=spec,
                        **value_data
                    )
            
            # ایجاد گزینه‌های محصول برای هر رنگ
            for color_name in product_data['colors']:
                color = Color.objects.get(name=color_name)
                option = ProductOption.objects.create(
                    product=product,
                    color=color,
                    option_price=product_data['base_price'],
                    quantity=random.randint(5, 20),
                    is_active=True
                )
                
                # اعمال تخفیف اگر محصول تخفیف دارد
                if product_data.get('has_discount', False):
                    discount_percentage = product_data.get('discount_percentage', 0)
                    if discount_percentage > 0:
                        option.is_active_discount = True
                        option.discount = discount_percentage
                        option.discount_start_date = timezone.now()
                        option.discount_end_date = timezone.now() + timedelta(days=30)
                        option.save()

                # ایجاد تصاویر گالری برای هر گزینه محصول
                for i in range(1, 4):  # ایجاد 3 تصویر برای هر گزینه
                    Gallery.objects.create(
                        product=option,
                        image=f'product_gallery/sample_{i}.jpg',  # تصویر نمونه
                        alt_text=f'{product.title} - {color_name} - تصویر {i}'
                    )
            
            products.append(product)

        self.stdout.write(f'{len(products)} products created.')

        self.stdout.write(self.style.SUCCESS('Successfully populated store data with realistic information!')) 