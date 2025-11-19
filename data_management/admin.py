from django.contrib import admin
from .models import ConcertSales


@admin.register(ConcertSales)
class ConcertSalesAdmin(admin.ModelAdmin):
    """콘서트 매출 Admin 설정"""
    
    # 목록 표시 필드
    list_display = [
        'performance',
        'date',
        'booking_site',
        'paid_revenue',
        'paid_ticket_count',
        'unpaid_revenue',
        'unpaid_ticket_count',
        'created_at',
    ]
    
    # 검색 필드
    search_fields = [
        'performance__title',
        'booking_site',
        'notes',
    ]
    
    # 필터
    list_filter = [
        'date',
        'booking_site',
        'performance',
        'created_at',
    ]
    
    # 날짜 계층
    date_hierarchy = 'date'
    
    # 필드 그룹화 (상세 페이지)
    fieldsets = (
        ('기본 정보', {
            'fields': ('performance', 'date', 'booking_site')
        }),
        ('유료 - 입금', {
            'fields': ('paid_revenue', 'paid_ticket_count', 'paid_by_grade')
        }),
        ('유료 - 미입금', {
            'fields': ('unpaid_revenue', 'unpaid_ticket_count', 'unpaid_by_grade')
        }),
        ('무료', {
            'fields': ('free_by_grade',)
        }),
        ('기타', {
            'fields': ('notes',)
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # 읽기 전용 필드
    readonly_fields = ['created_at', 'updated_at']
    
    # 정렬
    ordering = ['-date', 'performance', 'booking_site']
