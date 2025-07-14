from django.core.management.base import BaseCommand
from installments.models import InstallmentParameter, CompanyInstallmentParameter
from store.models import Category
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Generate fake data for InstallmentParameter and CompanyInstallmentParameter'

    def handle(self, *args, **options):
        categories = list(Category.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Found {len(categories)} categories.'))

        # Generate InstallmentParameter
        for i in range(5):
            method = random.choice([InstallmentParameter.METHOD_CHECK, InstallmentParameter.METHOD_PROMISSORY])
            repayment_period = random.choice([6, 12, 18, 24, 36])
            initial_increase_percent = Decimal(random.uniform(10, 40)).quantize(Decimal('0.01'))
            check_guarantee_period = random.choice([6, 12, 18, 24, 36])
            minimum_down_payment = Decimal(random.uniform(0, 5000000)).quantize(Decimal('0.01'))
            post_down_payment_increase_percent = Decimal(random.uniform(5, 20)).quantize(Decimal('0.01'))
            bank_tax_interest_percent = Decimal(random.uniform(0, 5)).quantize(Decimal('0.01'))
            param = InstallmentParameter.objects.create(
                method=method,
                repayment_period=repayment_period,
                initial_increase_percent=initial_increase_percent,
                check_guarantee_period=check_guarantee_period,
                minimum_down_payment=minimum_down_payment,
                post_down_payment_increase_percent=post_down_payment_increase_percent,
                bank_tax_interest_percent=bank_tax_interest_percent,
            )
            # Assign to random categories
            if categories:
                param.applicable_categories.set(random.sample(categories, k=random.randint(1, min(3, len(categories)))))
            self.stdout.write(self.style.SUCCESS(f'Created InstallmentParameter: {param}'))

        # Generate CompanyInstallmentParameter
        for i in range(5):
            repayment_period = random.choice([6, 12, 18, 24, 36])
            monthly_interest_percent = Decimal(random.uniform(0.5, 3)).quantize(Decimal('0.01'))
            minimum_down_payment = Decimal(random.uniform(0, 5000000)).quantize(Decimal('0.01'))
            guarantee_method = random.choice(['check', 'promissory', 'insurance'])
            param = CompanyInstallmentParameter.objects.create(
                repayment_period=repayment_period,
                monthly_interest_percent=monthly_interest_percent,
                minimum_down_payment=minimum_down_payment,
                guarantee_method=guarantee_method,
            )
            # Assign to random categories
            if categories:
                param.applicable_categories.set(random.sample(categories, k=random.randint(1, min(3, len(categories)))))
            self.stdout.write(self.style.SUCCESS(f'Created CompanyInstallmentParameter: {param}'))

        self.stdout.write(self.style.SUCCESS('Fake installment data generated successfully.')) 