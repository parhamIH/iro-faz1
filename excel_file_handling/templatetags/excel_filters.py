from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def percentage(value, total):
    """محاسبه درصد"""
    try:
        if total and total > 0:
            return floatformat((value / total) * 100, 0)
        return 0
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def divide(value, arg):
    """تقسیم دو عدد"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    """ضرب دو عدد"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def subtract(value, arg):
    """تفریق دو عدد"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """جمع دو عدد"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0 