from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random

from store.models import (
    Category, Product, Feature, InstallmentPlan,
    ProductFeature, ProductOption, Discount, Gallery, Color, Brand
)

class Command(BaseCommand):
    help = 'Populates the database with realistic store data'

    def handle(self, *args, **options):
        self.stdout.write('Deleting old data...')
        # ترتیب حذف مهم است به دلیل روابط ForeignKey
        Gallery.objects.all().delete()
        ProductOption.objects.all().delete()
        ProductFeature.objects.all().delete()
        InstallmentPlan.objects.all().delete()
        Product.objects.all().delete()
        Discount.objects.all().delete()
        Feature.objects.all().delete()
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
        # ویژگی‌های مشترک
        common_features = [
            {
                "name": "رنگ", 
                "type": "physical",
                "is_main_feature": True,
                "display_order": 1
            },
        ]
        
        # ویژگی‌های موبایل
        mobile_features = [
            {
                "name": "حافظه داخلی",
                "type": "technical",
                "unit": "گیگابایت",
                "is_main_feature": True,
                "display_order": 2
            },
            {
                "name": "رم",
                "type": "technical",
                "unit": "گیگابایت",
                "is_main_feature": True,
                "display_order": 3
            },
            {
                "name": "پردازنده",
                "type": "technical",
                "is_main_feature": True,
                "display_order": 4
            },
            {
                "name": "دوربین اصلی",
                "type": "technical",
                "unit": "مگاپیکسل",
                "is_main_feature": True,
                "display_order": 5
            },
        ]
        
        # ویژگی‌های لپ‌تاپ
        laptop_features = [
            {
                "name": "پردازنده",
                "type": "technical",
                "is_main_feature": True,
                "display_order": 2
            },
            {
                "name": "حافظه RAM",
                "type": "technical",
                "unit": "گیگابایت",
                "is_main_feature": True,
                "display_order": 3
            },
            {
                "name": "حافظه داخلی",
                "type": "technical",
                "unit": "گیگابایت",
                "is_main_feature": True,
                "display_order": 4
            },
            {
                "name": "کارت گرافیک",
                "type": "technical",
                "is_main_feature": True,
                "display_order": 5
            },
        ]
        
        # ویژگی‌های یخچال
        refrigerator_features = [
            {
                "name": "حجم کل",
                "type": "physical",
                "unit": "لیتر",
                "is_main_feature": True,
                "display_order": 2
            },
            {
                "name": "نوع یخچال",
                "type": "general",
                "is_main_feature": True,
                "display_order": 3
            },
            {
                "name": "برچسب انرژی",
                "type": "technical",
                "is_main_feature": True,
                "display_order": 4
            },
        ]
        
        # ویژگی‌های ماشین لباسشویی
        washing_machine_features = [
            {
                "name": "ظرفیت",
                "type": "physical",
                "unit": "کیلوگرم",
                "is_main_feature": True,
                "display_order": 2
            },
            {
                "name": "نوع موتور",
                "type": "technical",
                "is_main_feature": True,
                "display_order": 3
            },
            {
                "name": "تعداد برنامه شستشو",
                "type": "general",
                "is_main_feature": True,
                "display_order": 4
            },
            {
                "name": "برچسب انرژی",
                "type": "technical",
                "is_main_feature": True,
                "display_order": 5
            },
        ]

        features = []
        mobile_cat = Category.objects.get(name="موبایل")
        laptop_cat = Category.objects.get(name="لپ‌تاپ")
        refrigerator_cat = Category.objects.get(name="یخچال و فریزر")
        washing_cat = Category.objects.get(name="ماشین لباسشویی")

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

        # 5. Create Products with realistic data
        products_data = [
            {
                "title": "گوشی موبایل سامسونگ مدل Galaxy S23 Ultra",
                "base_price_cash": Decimal("45000000"),
                "description": "پرچمدار سامسونگ با دوربین 200 مگاپیکسلی",
                "category": mobile_cat,
                "brand": Brand.objects.get(name="سامسونگ"),
                "features": {
                    "حافظه داخلی": "256",
                    "رم": "12",
                    "پردازنده": "Snapdragon 8 Gen 2",
                    "دوربین اصلی": "200",
                    "رنگ": "مشکی"
                }
            },
            {
                "title": "لپ تاپ ایسوس مدل ROG Strix G15",
                "base_price_cash": Decimal("52000000"),
                "description": "لپ تاپ گیمینگ با پردازنده قدرتمند",
                "category": laptop_cat,
                "brand": Brand.objects.get(name="ایسوس"),
                "features": {
                    "پردازنده": "AMD Ryzen 9 5900HX",
                    "حافظه RAM": "32",
                    "حافظه داخلی": "1000",
                    "کارت گرافیک": "NVIDIA RTX 3070 8GB",
                    "رنگ": "مشکی"
                }
            },
            {
                "title": "یخچال و فریزر ساید بای ساید ال جی",
                "base_price_cash": Decimal("85000000"),
                "description": "یخچال و فریزر ساید بای ساید با تکنولوژی اینورتر",
                "category": refrigerator_cat,
                "brand": Brand.objects.get(name="ال جی"),
                "features": {
                    "حجم کل": "700",
                    "نوع یخچال": "ساید بای ساید",
                    "برچسب انرژی": "A++",
                    "رنگ": "نقره‌ای"
                }
            },
            {
                "title": "ماشین لباسشویی اسنوا مدل SWM-84518",
                "base_price_cash": Decimal("32000000"),
                "description": "ماشین لباسشویی 8 کیلویی اسنوا",
                "category": washing_cat,
                "brand": Brand.objects.get(name="اسنوا"),
                "features": {
                    "ظرفیت": "8",
                    "نوع موتور": "دایرکت درایو",
                    "تعداد برنامه شستشو": "16",
                    "برچسب انرژی": "A+++",
                    "رنگ": "سفید"
                }
            }
        ]

        products = []
        for product_data in products_data:
            # ایجاد محصول
            product = Product.objects.create(
                title=product_data['title'],
                base_price_cash=product_data['base_price_cash'],
                description=product_data['description'],
                brand=product_data['brand']
            )
            product.categories.add(product_data['category'])
            
            # اضافه کردن ویژگی‌ها
            features_data = product_data['features']
            for feature_name, value in features_data.items():
                feature = Feature.objects.get(name=feature_name, category=product_data['category'])
                ProductFeature.objects.create(
                    product=product,
                    feature=feature,
                    value=value
                )
            
            # اضافه کردن گزینه‌های رنگ
            color_feature = Feature.objects.get(name="رنگ", category=product_data['category'])
            color_value = features_data.get("رنگ")
            if color_value:
                color = Color.objects.get(name=color_value)
                ProductOption.objects.create(
                    product=product,
                    feature=color_feature,
                    value=color_value,
                    color=color,
                    option_price=0  # قیمت پایه برای رنگ اصلی
                )
            
            products.append(product)

        self.stdout.write(f'{len(products)} products created.')

        # 6. Create Discounts
        discount_data = [
            {
                "name": "تخفیف ویژه تابستان",
                "percentage": 15,
                "start_date": timezone.now(),
                "end_date": timezone.now() + timezone.timedelta(days=30)
            },
            {
                "name": "فروش فوق العاده",
                "percentage": 20,
                "start_date": timezone.now(),
                "end_date": timezone.now() + timezone.timedelta(days=15)
            }
        ]
        
        discounts = []
        for discount_info in discount_data:
            discount = Discount.objects.create(**discount_info)
            discounts.append(discount)
            
        self.stdout.write(f'{len(discounts)} discounts created.')

        # 7. Create InstallmentPlans for expensive products
        for product in products:
            if product.base_price_cash > Decimal('30000000'):  # فقط برای محصولات گران‌تر از 30 میلیون
                for months in [12, 24]:
                    plan = InstallmentPlan.objects.create(
                        title=f"طرح اقساطی {months} ماهه {product.title}",
                        product=product,
                        months=months,
                        prepayment=product.base_price_cash * Decimal('0.20')  # 20% پیش پرداخت
                    )
                    product.installment_plans.add(plan)

        self.stdout.write(self.style.SUCCESS('Successfully populated store data with realistic information!')) 