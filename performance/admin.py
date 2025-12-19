from django.contrib import admin
from .models import Performance, SeatGrade, BookingSite, DiscountType, Person, CrewRole, CastingRole


class SeatGradeInline(admin.TabularInline):
    """좌석 등급 인라인"""
    model = SeatGrade
    extra = 1
    fields = ['name', 'price', 'seat_count', 'order']
    ordering = ['order', 'name']


class BookingSiteInline(admin.TabularInline):
    """예매처 인라인"""
    model = BookingSite
    extra = 1
    fields = ['name', 'url']
    ordering = ['name']


class DiscountTypeInline(admin.TabularInline):
    """할인권종 인라인"""
    model = DiscountType
    extra = 1
    fields = ['name', 'start_date', 'end_date', 'discount_rate', 'applicable_grades']
    ordering = ['start_date', 'name']
    filter_horizontal = ['applicable_grades']


class CrewRoleInline(admin.TabularInline):
    """제작진 역할 인라인"""
    model = CrewRole
    extra = 1
    fields = ['person', 'role', 'order']
    ordering = ['order', 'role']


class CastingRoleInline(admin.TabularInline):
    """캐스팅 역할 인라인"""
    model = CastingRole
    extra = 1
    fields = ['person', 'role', 'order']
    ordering = ['order', 'role']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """인물 Admin 설정"""
    
    list_display = ['name', 'name_en', 'created_at']
    search_fields = ['name', 'name_en']
    ordering = ['name']


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
            'fields': ('producer', 'organizer')
        }),
        ('수익 목표', {
            'fields': ('target_revenue', 'break_even_point', 'total_production_cost')
        }),
        ('기타', {
            'fields': ('seat_map',)
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
    
    # 인라인
    inlines = [SeatGradeInline, BookingSiteInline, DiscountTypeInline, CrewRoleInline, CastingRoleInline]
