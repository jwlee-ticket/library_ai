from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def date_range(start, end):
    """날짜 범위 포맷팅"""
    if not start or not end:
        return ''
    
    try:
        start_str = start.strftime('%Y.%m.%d')
        end_str = end.strftime('%Y.%m.%d')
        return f'{start_str} ~ {end_str}'
    except (AttributeError, ValueError):
        return ''


@register.filter
def intcomma(value):
    """숫자에 세 자리마다 콤마 추가"""
    if value is None or value == '':
        return ''
    try:
        # Decimal이나 float인 경우 정수로 변환
        if hasattr(value, 'to_integral_value'):
            num = int(value.to_integral_value())
        else:
            num = int(float(value))
        return f'{num:,}'
    except (ValueError, TypeError):
        return str(value)

