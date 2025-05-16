from django.core.management.base import BaseCommand
from loan_calculator.models import LoanCondition, PrePaymentInstallment
from store.models import Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populates test data for loan calculator app'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating loan conditions...')

        # Dictionary of loan conditions for different product types
        loan_conditions_data = {
            'automobile': [
                {
                    'title': 'شرایط ویژه خودرو - 12 ماهه',
                    'condition_type': LoanCondition.ConditionTypeChoices.AUTOMOBILE,
                    'guarantee_type': LoanCondition.GuaranteeType.CHECK,
                    'has_guarantor': True,
                    'condition_months': 12,
                    'annual_interest_rate_percent': Decimal('24.00'),
                    'initial_increase_percent': Decimal('5.00'),
                    'single_prepayment_percent': Decimal('30.00'),
                    'secondary_increase_percent': Decimal('2.00'),
                    'delivery_days': 30,
                },
                {
                    'title': 'شرایط ویژه خودرو - 24 ماهه',
                    'condition_type': LoanCondition.ConditionTypeChoices.AUTOMOBILE,
                    'guarantee_type': LoanCondition.GuaranteeType.PROMISSORY,
                    'has_guarantor': True,
                    'condition_months': 24,
                    'annual_interest_rate_percent': Decimal('26.00'),
                    'initial_increase_percent': Decimal('7.00'),
                    'single_prepayment_percent': Decimal('40.00'),
                    'secondary_increase_percent': Decimal('3.00'),
                    'delivery_days': 60,
                }
            ],
            'general': [
                {
                    'title': 'شرایط عمومی - 6 ماهه',
                    'condition_type': LoanCondition.ConditionTypeChoices.GENERAL,
                    'guarantee_type': LoanCondition.GuaranteeType.CHECK,
                    'has_guarantor': False,
                    'condition_months': 6,
                    'annual_interest_rate_percent': Decimal('22.00'),
                    'initial_increase_percent': Decimal('3.00'),
                    'single_prepayment_percent': Decimal('20.00'),
                    'secondary_increase_percent': Decimal('1.00'),
                    'delivery_days': 7,
                },
                {
                    'title': 'شرایط عمومی - 12 ماهه با پیش‌پرداخت مرحله‌ای',
                    'condition_type': LoanCondition.ConditionTypeChoices.GENERAL,
                    'guarantee_type': LoanCondition.GuaranteeType.PROMISSORY,
                    'has_guarantor': True,
                    'condition_months': 12,
                    'annual_interest_rate_percent': Decimal('24.00'),
                    'initial_increase_percent': Decimal('4.00'),
                    'secondary_increase_percent': Decimal('2.00'),
                    'delivery_days': 21,
                    'prepayments': [
                        {'percent': Decimal('15.00'), 'days': 0, 'order': 0},
                        {'percent': Decimal('15.00'), 'days': 30, 'order': 1},
                        {'percent': Decimal('10.00'), 'days': 60, 'order': 2},
                    ]
                }
            ]
        }

        # Get all products starting from ID 6
        products = Product.objects.filter(id__gte=6)
        
        # Counter for created conditions
        conditions_created = 0
        prepayments_created = 0

        for product in products:
            # Determine which conditions to apply based on product category
            conditions_to_apply = []
            
            # Add automobile conditions for expensive products (price > 500,000,000)
            if product.base_price_cash > 500000000:
                conditions_to_apply.extend(loan_conditions_data['automobile'])
            
            # Add general conditions for all products
            conditions_to_apply.extend(loan_conditions_data['general'])

            # Create loan conditions for this product
            for condition_data in conditions_to_apply:
                prepayments = condition_data.pop('prepayments', None)
                
                condition = LoanCondition.objects.create(
                    product=product,
                    **condition_data
                )
                conditions_created += 1

                # Create prepayment installments if specified
                if prepayments:
                    for prepayment in prepayments:
                        PrePaymentInstallment.objects.create(
                            loan_condition=condition,
                            percent_of_initial_increased_price=prepayment['percent'],
                            days_offset_for_payment=prepayment['days'],
                            order=prepayment['order']
                        )
                        prepayments_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {conditions_created} loan conditions and {prepayments_created} prepayment installments'
        )) 