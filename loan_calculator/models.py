from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal, ROUND_CEILING
from datetime import date, timedelta # برای محاسبه تاریخ پیش‌پرداخت‌ها
from store.models import Product

class LoanCondition(models.Model):
    class GuaranteeType(models.TextChoices):
        PROMISSORY = 'promissory', _('سفته')
        CHECK = 'check', _('چک')
        # مقدار پیش‌فرض در جاوااسکریپت شما به نظر می‌رسد چک باشد
        DEFAULT = 'default', _('پیش‌فرض (چک)') 

    class ConditionTypeChoices(models.TextChoices):
        AUTOMOBILE = 'automobile', _('خودرو')
        GENERAL = 'general', _('عمومی')
        # سایر انواع شرایط را در صورت نیاز اضافه کنید

    product = models.ForeignKey(
        Product, 
        related_name='loan_conditions', 
        on_delete=models.SET_NULL, # یا CASCADE اگر شرایط بدون محصول بی‌معنی است
        verbose_name=_("محصول مرتبط"), 
        null=True, blank=True # اگر شرایط می‌تواند عمومی و بدون محصول خاص باشد
    )
    title = models.CharField(max_length=255, verbose_name=_("عنوان شرایط"))
    condition_type = models.CharField(
        max_length=50, 
        choices=ConditionTypeChoices.choices, 
        default=ConditionTypeChoices.GENERAL, 
        verbose_name=_("نوع شرایط")
    )
    
    guarantee_type = models.CharField(
        max_length=20, 
        choices=GuaranteeType.choices, 
        default=GuaranteeType.DEFAULT, 
        verbose_name=_("نوع ضمانت")
    )
    has_guarantor = models.BooleanField(default=False, verbose_name=_("نیاز به ضامن دارد؟"))
    
    condition_months = models.IntegerField(verbose_name=_("مدت اقساط (ماه)"))
    # نرخ سود سالانه برای محاسبات loanCalculation
    annual_interest_rate_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name=_("نرخ سود سالانه (%)")
    )
    
    # معادل condition.initialIncrease در JS
    initial_increase_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.0'), 
        verbose_name=_("درصد افزایش اولیه قیمت (%)")
    )
    
    # معادل condition.prePayment برای پیش‌پرداخت ساده و تکی
    single_prepayment_percent = models.DecimalField(
        max_digits=5, decimal_places=2, 
        null=True, blank=True, 
        verbose_name=_("درصد پیش‌پرداخت تکی (از قیمت پس از افزایش اولیه)")
    )
    
    # معادل condition.secondaryIncrease
    secondary_increase_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.0'), 
        verbose_name=_("درصد افزایش ثانویه (پس از پیش‌پرداخت) (%)")
    )
    
    delivery_days = models.IntegerField(default=0, verbose_name=_("زمان تحویل (روز)")) # 0 برای فوری

    @property
    def guarantor_status_display(self):
        """معادل hasGuarantorTitle در JS"""
        return _("دارد") if self.has_guarantor else _("ندارد")

    @property
    def delivery_title_display(self):
        """معادل createDeliveryTitle در JS"""
        days = self.delivery_days
        if days == 0: return _("فوری")
        if days == 3: return _("۷۲ ساعته")
        if days == 7: return _("۷ روزه") # مثال اضافه شده
        if days == 21: return _("۲۱ روزه")
        if days == 30: return _("۱ ماهه")
        if days == 60: return _("۲ ماهه")
        if days == 90: return _("سه ماهه")
        if days == 180: return _("۶ ماهه")
        if days == 270: return _("۹ ماهه")
        if days == 365: return _("۱ ساله")
        return _(f"{days} روزه") if days is not None else _("نامشخص")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("شرایط وام")
        verbose_name_plural = _("شرایط وام‌ها")

class PrePaymentInstallment(models.Model):
    """برای نگهداری پیش‌پرداخت‌های مرحله‌ای (condition.prePayments در JS)"""
    loan_condition = models.ForeignKey(
        LoanCondition, 
        related_name='prepayment_installments', 
        on_delete=models.CASCADE, 
        verbose_name=_("شرایط وام مرتبط")
    )
    # معادل prePayment.percent در JS
    percent_of_initial_increased_price = models.DecimalField(
        max_digits=5, decimal_places=2, 
        verbose_name=_("درصد از قیمت پس از افزایش اولیه")
    )
    # معادل prePayment.days در JS (فاصله زمانی از توافق)
    days_offset_for_payment = models.IntegerField(
        verbose_name=_("فاصله زمانی تا پرداخت (روز)")
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب پیش‌پرداخت"))

    @property
    def due_date_from_today(self):
        """تاریخ سررسید این قسط پیش‌پرداخت از امروز"""
        return date.today() + timedelta(days=self.days_offset_for_payment)

    def __str__(self):
        return _(f"پیش‌پرداخت {self.order + 1} برای {self.loan_condition.title} ({self.percent_of_initial_increased_price}%)")

    class Meta:
        ordering = ['loan_condition', 'order']
        verbose_name = _("قسط پیش‌پرداخت")
        verbose_name_plural = _("اقساط پیش‌پرداخت") 