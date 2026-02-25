from django.contrib import admin
from .models import (
    PerformanceDailySales,
    PerformanceFinalSales,
    PerformanceDailySalesGrade,
    PerformanceFinalSalesGrade,
    PerformanceSalesUploadLog,
    MusicalEpisodeSales,
)


class PerformanceDailySalesGradeInline(admin.TabularInline):
    """공연 데일리 등급별 판매 인라인"""
    model = PerformanceDailySalesGrade
    extra = 0
    fields = ['seat_grade', 'paid_count', 'unpaid_count', 'free_count']
    verbose_name = '등급별 판매'
    verbose_name_plural = '등급별 판매'


@admin.register(PerformanceDailySales)
class PerformanceDailySalesAdmin(admin.ModelAdmin):
    """공연 데일리 매출 Admin 설정"""
    
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
    inlines = [PerformanceDailySalesGradeInline]
    
    # 읽기 전용 필드
    readonly_fields = ['created_at', 'updated_at']
    
    # 정렬
    ordering = ['-date', 'performance', 'booking_site']


class PerformanceFinalSalesGradeInline(admin.TabularInline):
    """공연 최종 등급별 판매 인라인"""
    model = PerformanceFinalSalesGrade
    extra = 0
    fields = ['seat_grade', 'paid_count', 'unpaid_count', 'free_count', 'paid_revenue', 'total_revenue', 'paid_occupancy_rate', 'total_occupancy_rate']
    verbose_name = '등급별 판매'
    verbose_name_plural = '등급별 판매'


@admin.register(PerformanceFinalSales)
class PerformanceFinalSalesAdmin(admin.ModelAdmin):
    """공연 최종 매출 Admin 설정"""
    
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
    inlines = [PerformanceFinalSalesGradeInline]
    
    # 읽기 전용 필드
    readonly_fields = ['created_at', 'updated_at']
    
    # 정렬
    ordering = ['performance', 'booking_site']


@admin.register(PerformanceSalesUploadLog)
class PerformanceSalesUploadLogAdmin(admin.ModelAdmin):
    """공연 매출 업로드 기록 Admin 설정"""
    
    list_display = [
        'performance',
        'original_filename',
        'sheet_name',
        'date_start',
        'date_end',
        'status',
        'uploaded_at',
    ]
    list_filter = ['performance', 'status', 'uploaded_at']
    search_fields = ['performance__title', 'original_filename']
    readonly_fields = ['uploaded_at']


@admin.register(MusicalEpisodeSales)
class MusicalEpisodeSalesAdmin(admin.ModelAdmin):
    list_display = [
        'performance',
        'episode_no',
        'show_date',
        'show_time',
        'paid_ticket_count',
        'paid_revenue',
        'updated_at',
    ]
    list_filter = ['performance', 'show_date', 'upload_log']
    search_fields = ['performance__title', 'remark']
    ordering = ['performance', 'episode_no']
    readonly_fields = ['created_at', 'updated_at']
