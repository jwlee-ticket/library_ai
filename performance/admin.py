from django.contrib import admin
from .models import Performance


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    """공연 Admin 설정"""
    
    # 목록 표시 필드
    list_display = [
        'title',
        'genre',
        'venue',
        'performance_start',
        'performance_end',
        'sales_start',
        'sales_end',
        'created_at',
    ]
    
    # 검색 필드
    search_fields = [
        'title',
        'title_en',
        'venue',
        'producer',
        'organizer',
    ]
    
    # 필터
    list_filter = [
        'genre',
        'performance_start',
        'performance_end',
        'created_at',
    ]
    
    # 날짜 계층
    date_hierarchy = 'performance_start'
    
    # 필드 그룹화 (상세 페이지)
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'title_en', 'genre', 'venue')
        }),
        ('공연 일정', {
            'fields': ('performance_start', 'performance_end', 'sales_start', 'sales_end')
        }),
        ('상세 정보', {
            'fields': ('age_rating', 'running_time', 'description')
        }),
        ('제작 정보', {
            'fields': ('producer', 'organizer', 'crew', 'casting')
        }),
        ('수익 목표', {
            'fields': ('target_revenue', 'break_even_point', 'total_production_cost')
        }),
        ('좌석 및 가격', {
            'fields': ('seat_grades', 'ticket_prices', 'seat_counts', 'discount_types')
        }),
        ('예매 및 기타', {
            'fields': ('booking_sites', 'seat_map')
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # 읽기 전용 필드
    readonly_fields = ['created_at', 'updated_at']
    
    # 정렬
    ordering = ['-created_at']
