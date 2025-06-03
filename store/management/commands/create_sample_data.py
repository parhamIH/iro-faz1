from django.core.management.base import BaseCommand
from store.models import Product, Category, Brand, Color, ProductOption
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        # ایجاد برند‌ها
        brands = [
            Brand.objects.create(name="سامسونگ"),
            Brand.objects.create(name="اپل"),
            Brand.objects.create(name="شیائومی"),
            Brand.objects.create(name="هوآوی"),
        ]

        # ایجاد دسته‌بندی‌ها
        categories = [
            Category.objects.create(name="موبایل"),
            Category.objects.create(name="لپ تاپ"),
            Category.objects.create(name="تبلت"),
        ]

        # ایجاد رنگ‌ها
        colors = [
            Color.objects.create(name="مشکی", hex_code="#000000"),
            Color.objects.create(name="سفید", hex_code="#FFFFFF"),
            Color.objects.create(name="آبی", hex_code="#0000FF"),
            Color.objects.create(name="قرمز", hex_code="#FF0000"),
        ]

        # ایجاد محصولات
        products_data = [
            {
                "title": "گوشی سامسونگ گلکسی A54",
                "brand": brands[0],
                "description": "گوشی هوشمند سامسونگ با صفحه نمایش 6.4 اینچی",
                "price_range": (8_000_000, 12_000_000),
            },
            {
                "title": "آیفون 14 پرو مکس",
                "brand": brands[1],
                "description": "جدیدترین گوشی اپل با دوربین حرفه‌ای",
                "price_range": (45_000_000, 55_000_000),
            },
            {
                "title": "شیائومی ردمی نوت 12",
                "brand": brands[2],
                "description": "گوشی اقتصادی و قدرتمند شیائومی",
                "price_range": (7_000_000, 9_000_000),
            },
            {
                "title": "لپ تاپ سامسونگ گلکسی بوک 3",
                "brand": brands[0],
                "description": "لپ تاپ قدرتمند سامسونگ",
                "price_range": (35_000_000, 45_000_000),
            },
            {
                "title": "مک‌بوک ایر M2",
                "brand": brands[1],
                "description": "لپ تاپ فوق‌العاده باریک اپل",
                "price_range": (52_000_000, 65_000_000),
            },
        ]

        for data in products_data:
            # ایجاد محصول
            product = Product.objects.create(
                title=data["title"],
                brand=data["brand"],
                description=data["description"],
                is_active=True,
                total_sales=random.randint(0, 1000),
                rating=random.uniform(3.5, 5.0),
                views=random.randint(100, 10000),
            )

            # اضافه کردن دسته‌بندی
            if "لپ تاپ" in data["title"]:
                product.categories.add(categories[1])
            else:
                product.categories.add(categories[0])

            # ایجاد آپشن‌های محصول با رنگ‌های مختلف
            for color in random.sample(colors, k=random.randint(2, 4)):
                base_price = random.randint(data["price_range"][0], data["price_range"][1])
                has_discount = random.choice([True, False])
                
                ProductOption.objects.create(
                    product=product,
                    color=color,
                    option_price=base_price,
                    quantity=random.randint(0, 50),
                    is_active=True,
                    is_active_discount=has_discount,
                    discount=random.randint(5, 35) if has_discount else 0
                )

        self.stdout.write(self.style.SUCCESS('Successfully created sample data')) 