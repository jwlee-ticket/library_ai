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

