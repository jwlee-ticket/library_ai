from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
import json

register = template.Library()


@register.filter
def to_choices(value_list):
    """리스트를 [(value, value), ...] 형태의 튜플 리스트로 변환"""
    if not value_list:
        return []
    return [(item, item) for item in value_list]


@register.filter
def get_item(dictionary, key):
    """딕셔너리에서 키로 값을 가져오기"""
    if not dictionary:
        return ''
    try:
        return dictionary.get(key, '')
    except (AttributeError, TypeError):
        return ''


@register.filter
def genre_badge(genre_code):
    """장르 코드를 받아서 뱃지 HTML 반환"""
    genre_map = {
        'theater': {
            'name': '연극',
            'classes': 'bg-blue-100 text-blue-800'
        },
        'musical': {
            'name': '뮤지컬',
            'classes': 'bg-purple-100 text-purple-800'
        },
        'concert': {
            'name': '콘서트',
            'classes': 'bg-pink-100 text-pink-800'
        },
        'exhibition': {
            'name': '전시',
            'classes': 'bg-green-100 text-green-800'
        },
    }
    
    genre_info = genre_map.get(genre_code, {
        'name': genre_code,
        'classes': 'bg-gray-100 text-gray-800'
    })
    
    html = f'<span class="px-3 py-1 rounded-full text-sm font-medium {genre_info["classes"]}">{genre_info["name"]}</span>'
    return mark_safe(html)


@register.simple_tag
def display_json_list(json_data):
    """JSON 리스트 데이터를 표시"""
    if not json_data:
        return mark_safe('<span class="text-gray-400">없음</span>')
    
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        if not isinstance(data, list):
            return mark_safe('<span class="text-gray-400">잘못된 형식</span>')
        
        if len(data) == 0:
            return mark_safe('<span class="text-gray-400">없음</span>')
        
        items = ', '.join([f'<span class="px-2 py-1 bg-gray-100 rounded text-sm">{escape(str(item))}</span>' for item in data])
        html = f'<div class="flex flex-wrap gap-2">{items}</div>'
        return mark_safe(html)
    except (json.JSONDecodeError, TypeError):
        return mark_safe('<span class="text-red-500">데이터 오류</span>')


@register.simple_tag
def display_json_dict(json_data):
    """JSON 딕셔너리 데이터를 표시"""
    if not json_data:
        return mark_safe('<span class="text-gray-400">없음</span>')
    
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        if not isinstance(data, dict):
            return mark_safe('<span class="text-gray-400">잘못된 형식</span>')
        
        if len(data) == 0:
            return mark_safe('<span class="text-gray-400">없음</span>')
        
        items = []
        for key, value in data.items():
            if isinstance(value, dict):
                # 중첩 딕셔너리인 경우 (할인율 등)
                nested_items = ', '.join([f'{escape(str(k))}: {escape(str(v))}%' for k, v in value.items()])
                items.append(f'<div class="mb-2"><span class="font-medium text-gray-700">{escape(str(key))}:</span> <span class="text-gray-600">{nested_items}</span></div>')
            else:
                # 숫자인 경우 콤마 포맷팅
                display_value = str(value)
                try:
                    # 숫자로 변환 가능한지 확인
                    num_value = float(value)
                    if num_value == int(num_value):
                        # 정수인 경우 콤마 포맷팅
                        display_value = f'{int(num_value):,}'
                    else:
                        display_value = f'{num_value:,}'
                except (ValueError, TypeError):
                    pass
                items.append(f'<div class="mb-2"><span class="font-medium text-gray-700">{escape(str(key))}:</span> <span class="text-gray-600">{escape(display_value)}</span></div>')
        
        html = f'<div class="space-y-1">{chr(10).join(items)}</div>'
        return mark_safe(html)
    except (json.JSONDecodeError, TypeError):
        return mark_safe('<span class="text-red-500">데이터 오류</span>')


@register.simple_tag
def display_booking_sites(json_data):
    """예매처 JSON 데이터를 링크로 표시"""
    if not json_data:
        return mark_safe('<span class="text-gray-400">없음</span>')
    
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        if not isinstance(data, list):
            return mark_safe('<span class="text-gray-400">잘못된 형식</span>')
        
        if len(data) == 0:
            return mark_safe('<span class="text-gray-400">없음</span>')
        
        links = []
        for item in data:
            if isinstance(item, dict):
                for name, url in item.items():
                    links.append(f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer" class="text-primary hover:underline font-medium">{escape(str(name))}</a>')
            else:
                links.append(f'<span class="text-gray-600">{escape(str(item))}</span>')
        
        html = f'<div class="flex flex-wrap gap-3">{chr(10).join(links)}</div>'
        return mark_safe(html)
    except (json.JSONDecodeError, TypeError):
        return mark_safe('<span class="text-red-500">데이터 오류</span>')


@register.simple_tag
def display_discount_types(json_data):
    """할인권종 JSON 데이터를 표시"""
    if not json_data:
        return mark_safe('<span class="text-gray-400">없음</span>')
    
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        if not isinstance(data, list):
            return mark_safe('<span class="text-gray-400">잘못된 형식</span>')
        
        if len(data) == 0:
            return mark_safe('<span class="text-gray-400">없음</span>')
        
        items = []
        for item in data:
            if isinstance(item, dict):
                name = escape(str(item.get('name', '')))
                start_date = escape(str(item.get('start_date', '')))
                end_date = escape(str(item.get('end_date', '')))
                grade = escape(str(item.get('grade', '')))
                discount_rate = escape(str(item.get('discount_rate', 0)))
                
                # 한 행으로 표시: 이름 (기간, 좌석 등급, 할인율%)
                items.append(
                    f'<div class="mb-1 text-gray-700">'
                    f'{name} ({start_date} ~ {end_date}, {grade}, {discount_rate}%)'
                    f'</div>'
                )
            else:
                items.append(f'<div class="mb-1 text-gray-600">{escape(str(item))}</div>')
        
        html = f'<div class="space-y-1">{chr(10).join(items)}</div>'
        return mark_safe(html)
    except (json.JSONDecodeError, TypeError):
        return mark_safe('<span class="text-red-500">데이터 오류</span>')

