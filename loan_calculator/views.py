from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from decimal import Decimal, ROUND_CEILING, InvalidOperation
import math
from django.utils.translation import gettext_lazy as _

# Import مدل‌های خودتان
from .models import Product, LoanCondition, PrePaymentInstallment
# Import سریالایزرهای خودتان (اگر نیاز به لیست کردن یا ایجاد از طریق API دارید)
# from .serializers import ProductSerializer, LoanConditionSerializer

class LoanCalculatorViewSet(viewsets.ViewSet):
    """
    ViewSet برای محاسبات مربوط به وام و شرایط پرداخت.
    """

    def _calculate_loan_repayment_details(self, loan_price_decimal, annual_interest_rate_percent_decimal, return_months_int):
        """
        منطق تابع loanCalculation از JS.
        ورودی‌ها باید Decimal و int باشند.
        """
        if return_months_int <= 0:
            return {
                'monthly_payment': Decimal('0'),
                'total_payment': loan_price_decimal,
                'total_interest': Decimal('0'),
            }

        monthly_interest_rate = (annual_interest_rate_percent_decimal / Decimal('100')) / Decimal('12')
        
        if monthly_interest_rate == Decimal('0'):
            monthly_payment = loan_price_decimal / Decimal(return_months_int) if return_months_int > 0 else loan_price_decimal
        else:
            try:
                # Math.pow(1 + monthlyInterestRate, returnMonths)
                factor = (Decimal('1') + monthly_interest_rate) ** return_months_int
                if factor - Decimal('1') == Decimal('0'): # جلوگیری از تقسیم بر صفر
                    monthly_payment = loan_price_decimal / Decimal(return_months_int) if return_months_int > 0 else loan_price_decimal
                else:
                    monthly_payment = (loan_price_decimal * monthly_interest_rate * factor) / (factor - Decimal('1'))
            except InvalidOperation: # ممکن است در اثر اعداد بسیار بزرگ یا کوچک رخ دهد
                 monthly_payment = loan_price_decimal / Decimal(return_months_int) if return_months_int > 0 else loan_price_decimal


        total_payment = monthly_payment * Decimal(return_months_int)
        total_interest = total_payment - loan_price_decimal

        # Math.ceil معادل ROUND_CEILING در Decimal
        return {
            'monthly_payment': monthly_payment.quantize(Decimal('1'), rounding=ROUND_CEILING),
            'total_payment': total_payment.quantize(Decimal('1'), rounding=ROUND_CEILING),
            'total_interest': total_interest.quantize(Decimal('1'), rounding=ROUND_CEILING),
        }

    def _calculate_guarantee_price_decimal(self, base_price_for_guarantee_decimal, guarantee_type_str):
        """
        منطق تابع calculateGuaranteePrice از JS.
        ورودی‌ها باید Decimal و str باشند.
        """
        rate = Decimal('0.25') # پیش‌فرض از JS
        if guarantee_type_str == LoanCondition.GuaranteeType.PROMISSORY:
            rate = Decimal('0.50')
        elif guarantee_type_str == LoanCondition.GuaranteeType.CHECK: # این شاخه در JS اضافی بود چون پیش‌فرض همین است
            rate = Decimal('0.25')
        
        guarantee_price = base_price_for_guarantee_decimal + (base_price_for_guarantee_decimal * rate)
        return guarantee_price.quantize(Decimal('1'), rounding=ROUND_CEILING)


    @action(detail=False, methods=['post'], url_path='calculate-loan-offer')
    def calculate_loan_offer(self, request):
        """
        محاسبه کامل پیشنهاد وام بر اساس محصول، شرایط و پیش‌پرداخت احتمالی سفارشی.
        این اکشن منطق companyCalculation و سایر محاسبات مرتبط را ترکیب می‌کند.

        ورودی‌های مورد انتظار در request.data:
        - product_id (الزامی)
        - loan_condition_id (الزامی)
        - custom_prepayment_amount (اختیاری، مبلغ پیش‌پرداخت سفارشی)
        """
        product_id = request.data.get('product_id')
        condition_id = request.data.get('loan_condition_id')
        custom_prepayment_input = request.data.get('custom_prepayment_amount')

        if not product_id or not condition_id:
            return Response(
                {"error": _("product_id و loan_condition_id الزامی هستند.")}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(pk=product_id)
            condition = LoanCondition.objects.get(pk=condition_id)
        except Product.DoesNotExist:
            return Response({"error": _(f"محصول با شناسه {product_id} یافت نشد.")}, status=status.HTTP_404_NOT_FOUND)
        except LoanCondition.DoesNotExist:
            return Response({"error": _(f"شرایط وام با شناسه {condition_id} یافت نشد.")}, status=status.HTTP_404_NOT_FOUND)

        product_price = product.base_price
        
        # محاسبه قیمت پس از افزایش اولیه (initialIncrease در JS)
        price_after_initial_increase = product_price + (product_price * condition.initial_increase_percent / Decimal('100'))
        # در JS گرد کردن خاصی برای این مرحله نبود، اما معمولاً مقادیر پولی دو رقم اعشار دارند
        price_after_initial_increase = price_after_initial_increase.quantize(Decimal('0.01'))


        final_calculated_loan_price = Decimal('0')
        actual_total_prepayment_paid = Decimal('0')
        
        custom_prepayment_decimal = None
        if custom_prepayment_input is not None:
            try:
                custom_prepayment_decimal = Decimal(custom_prepayment_input)
                if custom_prepayment_decimal < Decimal('0'):
                    return Response({"error": _("مبلغ پیش‌پرداخت سفارشی نمی‌تواند منفی باشد.")}, status=status.HTTP_400_BAD_REQUEST)
            except InvalidOperation:
                return Response({"error": _("مبلغ پیش‌پرداخت سفارشی نامعتبر است.")}, status=status.HTTP_400_BAD_REQUEST)

        # --- تطبیق منطق companyCalculation ---
        if condition.condition_type == LoanCondition.ConditionTypeChoices.AUTOMOBILE:
            # اگر برای خودرو، پیش‌پرداخت‌های مرحله‌ای تعریف شده باشد (condition.prePayments در JS)
            installments = list(condition.prepayment_installments.all().order_by('order'))
            if installments:
                sum_of_installment_prepayments = Decimal('0')
                for inst in installments:
                    # (initialIncrease * prePayment.percent) / 100
                    installment_amount = (price_after_initial_increase * inst.percent_of_initial_increased_price / Decimal('100'))
                    sum_of_installment_prepayments += installment_amount.quantize(Decimal('0.01')) # جمع مبالغ گرد شده
                
                actual_total_prepayment_paid = sum_of_installment_prepayments
                remaining_price = price_after_initial_increase - actual_total_prepayment_paid
                final_calculated_loan_price = remaining_price + (remaining_price * condition.secondary_increase_percent / Decimal('100'))
            
            # اگر پیش‌پرداخت سفارشی برای خودرو داده شده باشد
            elif custom_prepayment_decimal is not None:
                actual_total_prepayment_paid = custom_prepayment_decimal
                remaining_price = price_after_initial_increase - actual_total_prepayment_paid
                final_calculated_loan_price = remaining_price + (remaining_price * condition.secondary_increase_percent / Decimal('100'))
            
            # اگر پیش‌پرداخت تکی (single_prepayment_percent) برای خودرو تعریف شده باشد
            elif condition.single_prepayment_percent is not None:
                actual_total_prepayment_paid = (price_after_initial_increase * condition.single_prepayment_percent / Decimal('100'))
                actual_total_prepayment_paid = actual_total_prepayment_paid.quantize(Decimal('0.01'))
                remaining_price = price_after_initial_increase - actual_total_prepayment_paid
                final_calculated_loan_price = remaining_price + (remaining_price * condition.secondary_increase_percent / Decimal('100'))
            else: # بدون هیچ پیش‌پرداختی برای خودرو
                actual_total_prepayment_paid = Decimal('0')
                # وام روی کل مبلغ پس از افزایش اولیه با اعمال افزایش ثانویه محاسبه می‌شود
                final_calculated_loan_price = price_after_initial_increase + (price_after_initial_increase * condition.secondary_increase_percent / Decimal('100'))
        
        else: # برای سایر انواع شرایط (غیر خودرو)
            if custom_prepayment_decimal is not None:
                actual_total_prepayment_paid = custom_prepayment_decimal
            elif condition.single_prepayment_percent is not None:
                actual_total_prepayment_paid = (price_after_initial_increase * condition.single_prepayment_percent / Decimal('100'))
                actual_total_prepayment_paid = actual_total_prepayment_paid.quantize(Decimal('0.01'))
            else: # بدون پیش‌پرداخت
                actual_total_prepayment_paid = Decimal('0')

            remaining_price_after_prepayment = price_after_initial_increase - actual_total_prepayment_paid
            
            if condition.secondary_increase_percent > Decimal('0'):
                final_calculated_loan_price = remaining_price_after_prepayment + \
                                         (remaining_price_after_prepayment * condition.secondary_increase_percent / Decimal('100'))
            else: # JS: loanPrice = initialIncrease - prePayment (یعنی loanPrice = remainPrice)
                final_calculated_loan_price = remaining_price_after_prepayment
        
        final_calculated_loan_price = final_calculated_loan_price.quantize(Decimal('0.01'))
        if final_calculated_loan_price < Decimal('0'): # مبلغ وام نمی‌تواند منفی باشد
            final_calculated_loan_price = Decimal('0')
        # --- پایان تطبیق منطق companyCalculation ---

        # محاسبه جزئیات بازپرداخت وام
        repayment_details = self._calculate_loan_repayment_details(
            final_calculated_loan_price,
            condition.annual_interest_rate_percent,
            condition.condition_months
        )

        # محاسبه مبلغ ضمانت
        # در JS، تابع calculateGuaranteePrice یک آرگومان price می‌گیرد.
        # باید مشخص شود این price، قیمت اولیه محصول است یا مبلغ نهایی وام یا قیمت پس از افزایش اولیه.
        # با توجه به اینکه در showAllPayment در کنار loanPrice نمایش داده می‌شود، ممکن است بر اساس قیمت اولیه محصول باشد.
        # اینجا فرض می‌کنیم بر اساس قیمت اولیه محصول (product.base_price) است.
        final_guarantee_amount = self._calculate_guarantee_price_decimal(
            product.base_price, # یا price_after_initial_increase یا final_calculated_loan_price ؟
            condition.guarantee_type
        )
        
        # جزئیات پیش‌پرداخت‌های مرحله‌ای (اگر وجود دارد)
        prepayment_installments_info = []
        if condition.condition_type == LoanCondition.ConditionTypeChoices.AUTOMOBILE and condition.prepayment_installments.exists():
            for inst in condition.prepayment_installments.all().order_by('order'):
                installment_price = (price_after_initial_increase * inst.percent_of_initial_increased_price / Decimal('100')).quantize(Decimal('1'), rounding=ROUND_CEILING)
                prepayment_installments_info.append({
                    "percent": float(inst.percent_of_initial_increased_price), # معادل prePayment.percent
                    "price_rounded": float(installment_price), # معادل prePayment.prepaymentPrice
                    "days_offset": inst.days_offset_for_payment, # معادل prePayment.days
                    "due_date_from_today": inst.due_date_from_today.strftime("%Y-%m-%d") # مشابه getDate(addDays(...))
                })


        # آماده‌سازی پاسخ نهایی مشابه ساختار row در showAllPayment
        response_data = {
            "product_id": product.id,
            "product_name": product.name,
            "condition_id": condition.id,
            "condition_title": condition.title,
            "initial_product_price": float(product.base_price), # قیمت خام محصول
            "initial_increase_percent_applied": float(condition.initial_increase_percent), # درصد افزایش اولیه
            "price_after_initial_increase": float(price_after_initial_increase), # مبلغ پس از افزایش اولیه (initialIncreasePrice در JS)
            
            # درصد پیش‌پرداخت موثر (مشابه آنچه در جدول JS نمایش داده می‌شود)
            "effective_prepayment_percent": float((actual_total_prepayment_paid / price_after_initial_increase * 100).quantize(Decimal('0.01'))) if price_after_initial_increase > 0 else 0,
            "total_prepayment_paid_amount": float(actual_total_prepayment_paid.quantize(Decimal('0.01'))), # مبلغ کل پیش‌پرداخت (prePaymentPrice در JS)
            
            "prepayment_installments_details": prepayment_installments_info if prepayment_installments_info else None,

            "secondary_increase_percent_applied": float(condition.secondary_increase_percent), # درصد افزایش ثانویه
            "final_loan_amount": float(final_calculated_loan_price), # مبلغ تسهیلات (loanPrice)
            
            "monthly_payment": float(repayment_details['monthly_payment']), # مبلغ قسط
            "total_loan_payment_over_term": float(repayment_details['total_payment']), # کل بازپرداخت وام
            "total_loan_interest_over_term": float(repayment_details['total_interest']), # کل سود وام
            
            "guarantee_amount_calculated": float(final_guarantee_amount), # مبلغ چک/سفته ضمانت
            "guarantee_type_required": condition.get_guarantee_type_display(),
            "guarantor_needed_display": condition.guarantor_status_display,
            
            "loan_duration_months": condition.condition_months, # مدت اقساط
            "delivery_time_display": condition.delivery_title_display, # تحویل
        }

        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='available-payment-months')
    def get_available_payment_months(self, request):
        """
        مشابه showPaymentMonths برای گرفتن لیست ماه‌های پرداخت موجود.
        می‌تواند یک پارامتر condition_type برای فیلتر کردن بپذیرد.
        """
        condition_type_filter = request.query_params.get('condition_type')
        
        qs = LoanCondition.objects.all()
        if condition_type_filter:
            # اطمینان از اینکه مقدار condition_type_filter معتبر است
            valid_types = [choice[0] for choice in LoanCondition.ConditionTypeChoices.choices]
            if condition_type_filter in valid_types:
                qs = qs.filter(condition_type=condition_type_filter)
            else:
                return Response({"error": _(f"نوع شرایط نامعتبر: {condition_type_filter}")}, status=status.HTTP_400_BAD_REQUEST)

        # distinct().order_by() برای گرفتن ماه‌های یکتا و مرتب شده
        months = sorted(list(set(qs.values_list('condition_months', flat=True))))
        
        return Response({"available_months": months})

    # اکشن برای تولید PDF می‌تواند اینجا اضافه شود.
    # از کتابخانه‌ای مانند ReportLab یا WeasyPrint استفاده خواهد کرد.
    # منطق استایل‌دهی از pdfTableLayout باید به API کتابخانه PDF نگاشت شود.
    # متن‌های فارسی با s[::-1] معکوس می‌شوند.
    # @action(detail=False, methods=['post'], url_path='generate-loan-summary-pdf')
    # def generate_loan_summary_pdf(self, request):
    # # 1. دریافت ورودی‌ها (مثلاً product_id, loan_condition_id, custom_prepayment_amount)
    # # 2. فراخوانی منطق مشابه calculate_loan_offer برای گرفتن داده‌ها
    # # 3. استفاده از کتابخانه PDF برای ساخت PDF
    # # - ایجاد جدول با داده‌ها
    # # - اعمال استایل‌ها (رنگ پس‌زمینه ردیف‌های زوج/فرد، خطوط جدول و ...)
    # # - معکوس کردن متن‌های فارسی برای نمایش صحیح
    # # 4. بازگرداندن HttpResponse با محتوای PDF
    # pass 