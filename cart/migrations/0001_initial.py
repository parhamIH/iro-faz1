# Generated by Django 5.2.1 on 2025-07-17 10:28

import cart.models
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("store", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Cart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "session_key",
                    models.CharField(
                        blank=True, db_index=True, max_length=40, null=True
                    ),
                ),
                ("is_paid", models.BooleanField(default=False)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("count", models.PositiveIntegerField(default=1)),
                (
                    "final_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=12, null=True
                    ),
                ),
                ("added_date", models.DateTimeField(auto_now_add=True)),
                (
                    "cart",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cart.cart"
                    ),
                ),
                (
                    "package",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="store.productoption",
                    ),
                ),
            ],
            options={
                "ordering": ["-added_date"],
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "session_key",
                    models.CharField(
                        blank=True, db_index=True, max_length=40, null=True
                    ),
                ),
                (
                    "order_number",
                    models.CharField(
                        default=cart.models.generate_order_number,
                        editable=False,
                        max_length=100,
                        unique=True,
                    ),
                ),
                ("order_date", models.DateTimeField(auto_now_add=True)),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("online", "پرداخت آنلاین"),
                            ("wallet", "کیف پول"),
                            ("cod", "پرداخت در محل"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "payment_status",
                    models.CharField(
                        choices=[
                            ("پرداخت شده", "پرداخت شده"),
                            ("در انتظار پرداخت", "در انتظار پرداخت"),
                            ("در انتظار تایید", "در انتظار تایید"),
                            ("ناموفق", "ناموفق"),
                            ("لغو شده", "لغو شده"),
                        ],
                        default="در انتظار پرداخت",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("در حال انتظار", "در حال انتظار"),
                            ("در حال پردازش", "در حال پردازش"),
                            ("ارسال شده", "ارسال شده"),
                            ("تحویل داده شده", "تحویل داده شده"),
                            ("لغو شده", "لغو شده"),
                        ],
                        default="در حال انتظار",
                        max_length=20,
                    ),
                ),
                (
                    "shipping_method",
                    models.CharField(
                        choices=[
                            ("post", "پست"),
                            ("tipax", "تیپاکس"),
                            ("express", "پیک موتوری"),
                        ],
                        default="post",
                        max_length=20,
                    ),
                ),
                (
                    "shipping_cost",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=10
                    ),
                ),
                (
                    "total_price",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=14
                    ),
                ),
                (
                    "discount_code",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "discount_amount",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                ("shipping_date", models.DateTimeField(blank=True, null=True)),
                ("delivery_date", models.DateField(blank=True, null=True)),
                (
                    "jalali_delivery_date",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "cart",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT, to="cart.cart"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="cart",
            index=models.Index(
                fields=["session_key"], name="cart_cart_session_5e1af5_idx"
            ),
        ),
    ]
