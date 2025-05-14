from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random

from store.models import (
    Category, Product, Feature, InstallmentPlan,
    ProductFeatureValue, ProductOption, Discount, Gallery, Color, Brand
)
# اگر از Faker استفاده می‌کنید، آن را اینجا import کنید
# from faker import Faker
# fake = Faker('fa_IR') # برای داده‌های فارسی

class Command(BaseCommand):
    help = 'Populates the database with fake store data for the store app'

    def handle(self, *args, **options):
        self.stdout.write('Deleting old data...')
        # ترتیب حذف مهم است به دلیل روابط ForeignKey
        Gallery.objects.all().delete()
        ProductOption.objects.all().delete()
        ProductFeatureValue.objects.all().delete()
        InstallmentPlan.objects.all().delete() # تخفیف‌ها از طریق این مدل هم مرتبط هستند
        Product.objects.all().delete() # دسته‌بندی‌ها و تخفیف‌ها از طریق این مدل هم مرتبط هستند
        Discount.objects.all().delete()
        Feature.objects.all().delete()
        Color.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Old data deleted.'))

        self.stdout.write('Starting to populate data...')
        # 1. Create Brands
        brands_data = [
            {"name": "سامسونگ", "description": "سامسونگ"},
            {"name": "ایسوس", "description": "ایسوس"},
            {"name": "دیور", "description": "دیور"},
            {"name": "وسترن", "description": "وسترن"},
        ]
        
        brands = [] 
        for b_data in brands_data:
            brand, _ = Brand.objects.get_or_create(**b_data)
            brands.append(brand)
        self.stdout.write(f'{len(brands)} brands created.')
        
        # 1. Create Colors
        colors_data = [
            {"name": "سفید", "hex_code": "#FFFFFF"},
            {"name": "مشکی", "hex_code": "#000000"},
            {"name": "قرمز", "hex_code": "#FF0000"},
            {"name": "آبی", "hex_code": "#0000FF"},
            {"name": "سبز", "hex_code": "#008000"},
            {"name": "خاکستری", "hex_code": "#808080"},
            {"name": "نقره ای", "hex_code": "#C0C0C0"},
        ]
        colors = []
        for c_data in colors_data:
            color, _ = Color.objects.get_or_create(hex_code=c_data['hex_code'], defaults=c_data)
            colors.append(color)
        self.stdout.write(f'{len(colors)} colors created.')

        # 2. Create Categories
        categories_data = [
            {"name": "کالای دیجیتال", "description": "انواع کالاهای دیجیتال"},
            {"name": "موبایل", "description": "انواع گوشی‌های هوشمند و ساده"},
            {"name": "لپ‌تاپ", "description": "انواع لپ‌تاپ و نوت‌بوک"},
            {"name": "لوازم جانبی کامپیوتر", "description": "کیبورد، ماوس، و غیره"},
            {"name": "لوازم خانگی", "description": "انواع لوازم برقی و غیر برقی خانگی"},
            {"name": "تلویزیون", "description": "انواع تلویزیون هوشمند و عادی"},
        ]
        categories = []
        parent_digital = None
        for i, cat_data in enumerate(categories_data):
            if cat_data['name'] == "کالای دیجیتال":
                category = Category.objects.create(**cat_data)
                parent_digital = category
            elif cat_data['name'] in ["موبایل", "لپ‌تاپ", "لوازم جانبی کامپیوتر"]:
                category = Category.objects.create(parent=parent_digital, **cat_data)
            else:
                category = Category.objects.create(**cat_data)
            categories.append(category)
        self.stdout.write(f'{len(categories)} categories created.')

        # 3. Create Features
        features_data = ["پردازنده", "رم", "حافظه داخلی", "اندازه صفحه نمایش", "دوربین اصلی", "سیستم عامل", "رنگبندی"]
        features = []
        for f_name in features_data:
            feature, _ = Feature.objects.get_or_create(name=f_name)
            features.append(feature)
        self.stdout.write(f'{len(features)} features created.')

        # 4. Create Discounts
        discounts = []
        for i in range(3):
            discount = Discount.objects.create(
                name=f"تخفیف ویژه {i+1}",
                percentage=random.randint(5, 25),
                start_date=timezone.now() - timezone.timedelta(days=random.randint(-5, 5)), # Some active, some not
                end_date=timezone.now() + timezone.timedelta(days=random.randint(1, 30))
            )
            discounts.append(discount)
        self.stdout.write(f'{len(discounts)} discounts created.')

        # 5. Create Products
        products = []
        product_titles = [
            "گوشی موبایل سامسونگ گلکسی A54", "لپ تاپ ۱۵ اینچی ایسوس مدل VivoBook R565EA",
            "تلویزیون هوشمند ۴۳ اینچ اسنوا", "هارد اکسترنال وسترن دیجیتال ۲ ترابایت",
            "کیبورد و ماوس بی‌سیم لاجیتک", "یخچال فریزر ساید بای ساید دوو"
        ]
        for i in range(len(product_titles)):
            product = Product.objects.create(
                title=product_titles[i],
                base_price_cash=Decimal(random.randrange(5000000, 50000000, 100000)),
                description=f"توضیحات کامل برای {product_titles[i]}. این محصول دارای ویژگی‌های منحصر به فردی است.",
                # image='path/to/your/placeholder_image.jpg' # در صورت نیاز
            )
            # Assign categories (randomly assign 1 or 2 categories)
            product_cats = random.sample(categories, k=random.randint(1, min(2, len(categories))))
            product.categories.set(product_cats)
            
            # Assign some discounts (optional)
            if random.choice([True, False]):
                 product.discounts.set(random.sample(discounts, k=random.randint(1, min(2,len(discounts)))))
            products.append(product)
        self.stdout.write(f'{len(products)} products created.')

        # 6. Create Installment Plans
        installment_plans = []
        for product_obj in products:
            if not product_obj.categories.filter(name__in=["موبایل", "لپ‌تاپ", "تلویزیون", "یخچال فریزر ساید بای ساید دوو"]).exists():
                continue # فقط برای برخی دسته‌بندی‌ها طرح اقساطی ایجاد کن

            for j in range(random.randint(1, 2)): # 1 or 2 plans per product
                selected_months = random.choice(InstallmentPlan.SELECT_MONTHS)[0]
                plan = InstallmentPlan.objects.create(
                    title=f"طرح {selected_months} ماهه برای {product_obj.title[:20]}",
                    product=product_obj,
                    months=selected_months,
                    prepayment=product_obj.base_price_cash * Decimal(random.choice(['0.1', '0.2', '0.25']))
                )
                # Assign some discounts to plan (optional)
                if random.choice([True, False, False]): # Less likely
                    plan.discounts.set(random.sample(discounts, k=random.randint(1,min(1,len(discounts)))))
                installment_plans.append(plan)
                product_obj.installment_plans.add(plan) # Add to product's m2m
        self.stdout.write(f'{len(installment_plans)} installment plans created.')


        # 7. Create ProductFeatureValues
        product_feature_values = []
        feature_value_samples = {
            "پردازنده": ["Core i5", "Snapdragon 8 Gen 2", "Core i7", "Helio G99"],
            "رم": ["8GB", "16GB", "12GB", "6GB"],
            "حافظه داخلی": ["256GB SSD", "128GB", "512GB", "1TB HDD"],
            "اندازه صفحه نمایش": ["6.5 اینچ", "15.6 اینچ", "43 اینچ", "27 اینچ"],
            "دوربین اصلی": ["50MP", "12MP", "108MP", "64MP"],
            "سیستم عامل": ["Android 13", "Windows 11", "WebOS", "بدون سیستم عامل"],
            "رنگبندی": ["مشکی، سفید، آبی", "نقره‌ای، خاکستری", "فقط مشکی"]
        }
        for product_obj in products:
            num_features_to_add = random.randint(2, min(5, len(features)))
            added_features = []
            for _ in range(num_features_to_add):
                feature_obj = random.choice([f for f in features if f not in added_features])
                added_features.append(feature_obj)
                if feature_obj.name in feature_value_samples:
                    value = random.choice(feature_value_samples[feature_obj.name])
                    pfv = ProductFeatureValue.objects.create(
                        product=product_obj,
                        feature=feature_obj,
                        value=value
                    )
                    product_feature_values.append(pfv)
        self.stdout.write(f'{len(product_feature_values)} product feature values created.')

        # 8. Create ProductOptions
        product_options = []
        for product_obj in products:
            # Add color options if product has color feature
            color_feature = Feature.objects.filter(name__icontains="رنگ").first()
            if color_feature and ProductFeatureValue.objects.filter(product=product_obj, feature=color_feature).exists():
                for _ in range(random.randint(1,3)): # 1 to 3 color options
                    selected_color = random.choice(colors)
                    # Check if this option already exists for this product and feature (color)
                    existing_option = ProductOption.objects.filter(product=product_obj, feature=color_feature, color=selected_color).first()
                    if not existing_option:
                        po = ProductOption.objects.create(
                            product=product_obj,
                            feature=color_feature,
                            value=selected_color.name, # Value can be color name
                            color=selected_color,
                            price_change=Decimal(random.randrange(-50000, 50000, 10000)) # +/- 500k Rials
                        )
                        product_options.append(po)
        self.stdout.write(f'{len(product_options)} product options created.')

        # 9. Create Gallery Items
        gallery_items = []
        for product_option in product_options:  # iterate over product options instead of products
            for i in range(random.randint(1, 4)):  # 1 to 4 images per product option
                # image='path/to/your/gallery_image_{i}.jpg' # در صورت نیاز
                item = Gallery.objects.create(
                    product=product_option,  # now correctly using ProductOption
                    alt_text=f"نمای {i+1} از {product_option.product.title} - {product_option.value}"
                )
                gallery_items.append(item)
        self.stdout.write(f'{len(gallery_items)} gallery items created.')

        self.stdout.write(self.style.SUCCESS('Successfully populated store data!')) 