from django.db import models
from django.core.validators import MinValueValidator


class Performance(models.Model):
    """공연 모델"""
    
    # 장르 선택지
    GENRE_CHOICES = [
        ('theater', '연극'),
        ('musical', '뮤지컬'),
        ('concert', '콘서트'),
        ('exhibition', '전시'),
    ]
    
    # 필수 텍스트 필드
    title = models.CharField(max_length=200, verbose_name='공연명')
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, verbose_name='장르')
    venue = models.CharField(max_length=200, verbose_name='공연장')
    
    # 선택 텍스트 필드
    title_en = models.CharField(max_length=200, blank=True, verbose_name='공연명(영문)')
    age_rating = models.CharField(max_length=50, blank=True, verbose_name='관람 연령')
    running_time = models.CharField(max_length=50, blank=True, verbose_name='러닝 타임')
    producer = models.CharField(max_length=200, blank=True, verbose_name='제작/주최')
    organizer = models.CharField(max_length=200, blank=True, verbose_name='주관')
    description = models.TextField(blank=True, verbose_name='설명')
    
    # 필수 날짜 필드
    performance_start = models.DateField(verbose_name='공연 시작일')
    performance_end = models.DateField(verbose_name='공연 종료일')
    sales_start = models.DateField(verbose_name='판매 시작일')
    sales_end = models.DateField(verbose_name='판매 종료일')
    
    # 수익 목표 필드
    target_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='목표 금액 (원)',
        help_text='공연의 목표 매출액'
    )
    break_even_point = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='손익분기점 (원)',
        help_text='손익분기점 매출액'
    )
    total_production_cost = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='총 제작비 (원)',
        help_text='총 제작비용'
    )
    
    # JSON 필드 (리스트)
    seat_grades = models.JSONField(default=list, blank=True, verbose_name='좌석 등급')
    # 예시: ["VIP", "R석", "S석"]
    
    crew = models.JSONField(default=dict, blank=True, verbose_name='제작진')
    # 예시: {"감독": "홍길동", "음악": "김철수"}
    
    booking_sites = models.JSONField(default=list, blank=True, verbose_name='예매처')
    # 예시: [{"인터파크": "https://..."}, {"예스24": "https://..."}]
    
    # JSON 필드 (딕셔너리)
    ticket_prices = models.JSONField(default=dict, blank=True, verbose_name='티켓 가격')
    # 예시: {"VIP": 150000, "R석": 100000}
    
    seat_counts = models.JSONField(default=dict, blank=True, verbose_name='좌석 수')
    # 예시: {"VIP": 50, "R석": 200}
    
    discounts = models.JSONField(default=dict, blank=True, verbose_name='할인율')
    # 예시: {"VIP": {"조조할인": 10, "단체할인": 15}}
    
    casting = models.JSONField(default=dict, blank=True, verbose_name='캐스팅')
    # 예시: {"홍길동": "배우A", "김철수": "배우B"}
    
    # 이미지 필드
    seat_map = models.ImageField(
        upload_to='seat_maps/',
        null=True,
        blank=True,
        verbose_name='좌석배치도'
    )
    
    # 메타 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        verbose_name = '공연'
        verbose_name_plural = '공연들'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['genre']),
            models.Index(fields=['performance_start', 'performance_end']),
        ]
    
    def __str__(self):
        return self.title
