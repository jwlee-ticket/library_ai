from django.contrib import admin
from .models import ConcertDailySales, ConcertFinalSales, ConcertDailySalesGrade, ConcertFinalSalesGrade


class ConcertDailySalesGradeInline(admin.TabularInline):
    """콘서트 데일리 등급별 판매 인라인"""
    model = ConcertDailySalesGrade
    extra = 0
    fields = ['seat_grade', 'paid_count', 'unpaid_count', 'free_count']
    verbose_name = '등급별 판매'
    verbose_name_plural = '등급별 판매'


@admin.register(ConcertDailySales)
class ConcertDailySalesAdmin(admin.ModelAdmin):
    """콘서트 데일리 매출 Admin 설정"""
    
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
        'booking_site__name',
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
            'fields': ('paid_revenue', 'paid_ticket_count')
        }),
        ('유료 - 미입금', {
            'fields': ('unpaid_revenue', 'unpaid_ticket_count')
        }),
        ('기타', {
            'fields': ('notes',)
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # 인라인
    inlines = [ConcertDailySalesGradeInline]
    
    # 읽기 전용 필드
    readonly_fields = ['created_at', 'updated_at']
    
    # 정렬
    ordering = ['-date', 'performance', 'booking_site']


class ConcertFinalSalesGradeInline(admin.TabularInline):
    """콘서트 최종 등급별 판매 인라인"""
    model = ConcertFinalSalesGrade
    extra = 0
    fields = ['seat_grade', 'paid_count', 'unpaid_count', 'free_count', 'paid_revenue', 'total_revenue', 'paid_occupancy_rate', 'total_occupancy_rate']
    verbose_name = '등급별 판매'
    verbose_name_plural = '등급별 판매'


@admin.register(ConcertFinalSales)
class ConcertFinalSalesAdmin(admin.ModelAdmin):
    """콘서트 최종 매출 Admin 설정"""
    
    # 목록 표시 필드
    list_display = [
        'performance',
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
        'booking_site__name',
        'notes',
    ]
    
    # 필터
    list_filter = [
        'booking_site',
        'performance',
        'created_at',
    ]
    
    # 필드 그룹화 (상세 페이지)
    fieldsets = (
        ('기본 정보', {
            'fields': ('performance', 'booking_site')
        }),
        ('유료 - 입금', {
            'fields': ('paid_revenue', 'paid_ticket_count')
        }),
        ('유료 - 미입금', {
            'fields': ('unpaid_revenue', 'unpaid_ticket_count')
        }),
        ('기타', {
            'fields': ('notes',)
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # 인라인
    inlines = [ConcertFinalSalesGradeInline]
    
    # 읽기 전용 필드
    readonly_fields = ['created_at', 'updated_at']
    
    # 정렬
    ordering = ['performance', 'booking_site']
