from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from store.models import Product
from loan_calculator.models import LoanCondition, PrePaymentInstallment

class Command(BaseCommand):
    help = 'Populates the database with sample loan data'

    def handle(self, *args, **options):
        self.stdout.write('Deleting old loan data...')
        PrePaymentInstallment.objects.all().delete()
        LoanCondition.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Old loan data deleted.'))

        self.stdout.write('Starting to populate loan data...')

        # شرایط وام برای محصولات دیجیتال
        digital_conditions = [
            {
                'title': 'طرح اقساطی 12 ماهه دیجیتال',
                'condition_type': 'digital',
                'guarantee_type': 'check',
                'has_guarantor': True,
                'condition_months': 12,
                'annual_interest_rate_percent': Decimal('24.00'),
                'initial_increase_percent': Decimal('10.00'),
                'single_prepayment_percent': Decimal('30.00'),
                'secondary_increase_percent': Decimal('5.00'),
                'delivery_days': 7
            },
            {
                'title': 'طرح اقساطی 24 ماهه دیجیتال',
                'condition_type': 'digital',
                'guarantee_type': 'promissory',
                'has_guarantor': True,
                'condition_months': 24,
                'annual_interest_rate_percent': Decimal('28.00'),
                'initial_increase_percent': Decimal('15.00'),
                'single_prepayment_percent': Decimal('40.00'),
                'secondary_increase_percent': Decimal('8.00'),
                'delivery_days': 14
            }
        ]

        # شرایط وام برای محصولات عمومی
        general_conditions = [
            {
                'title': 'طرح اقساطی 6 ماهه عمومی',
                'condition_type': 'general',
                'guarantee_type': 'check',
                'has_guarantor': False,
                'condition_months': 6,
                'annual_interest_rate_percent': Decimal('18.00'),
                'initial_increase_percent': Decimal('5.00'),
                'single_prepayment_percent': Decimal('20.00'),
                'secondary_increase_percent': Decimal('3.00'),
                'delivery_days': 3
            },
            {
                'title': 'طرح اقساطی 12 ماهه عمومی',
                'condition_type': 'general',
                'guarantee_type': 'check',
                'has_guarantor': True,
                'condition_months': 12,
                'annual_interest_rate_percent': Decimal('22.00'),
                'initial_increase_percent': Decimal('8.00'),
                'single_prepayment_percent': Decimal('25.00'),
                'secondary_increase_percent': Decimal('4.00'),
                'delivery_days': 7
            }
        ]

        loan_conditions = []
        
        # ایجاد شرایط وام برای محصولات دیجیتال
        digital_products = Product.objects.filter(categories__name__in=['موبایل', 'لپ‌تاپ'])
        for product in digital_products:
            for condition_data in digital_conditions:
                condition = LoanCondition.objects.create(
                    product=product,
                    **condition_data
                )
                loan_conditions.append(condition)

                # ایجاد پیش‌پرداخت‌های مرحله‌ای
                if condition.condition_months > 12:
                    PrePaymentInstallment.objects.create(
                        loan_condition=condition,
                        percent_of_initial_increased_price=Decimal('20.00'),
                        days_offset_for_payment=0,
                        order=0
                    )
                    PrePaymentInstallment.objects.create(
                        loan_condition=condition,
                        percent_of_initial_increased_price=Decimal('20.00'),
                        days_offset_for_payment=30,
                        order=1
                    )

        # ایجاد شرایط وام برای محصولات عمومی
        general_products = Product.objects.exclude(id__in=digital_products.values_list('id', flat=True))
        for product in general_products:
            for condition_data in general_conditions:
                condition = LoanCondition.objects.create(
                    product=product,
                    **condition_data
                )
                loan_conditions.append(condition)

        self.stdout.write(f'{len(loan_conditions)} loan conditions created.')
        self.stdout.write(self.style.SUCCESS('Successfully populated loan data!')) 