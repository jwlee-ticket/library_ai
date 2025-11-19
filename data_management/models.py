from django.db import models
from django.core.validators import MinValueValidator


class ConcertDailySales(models.Model):
    """콘서트 데일리 매출 모델"""
    
    performance = models.ForeignKey(
        'performance.Performance',
        on_delete=models.CASCADE,
        limit_choices_to={'genre': 'concert'},
        verbose_name='공연',
        related_name='daily_sales'
    )
    date = models.DateField(verbose_name='공연 날짜')
    booking_site = models.CharField(max_length=100, verbose_name='예매처')
    
    # 유료 - 입금
    paid_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='입금 판매액 (원)',
        help_text='예매처별(입금) 판매액'
    )
    paid_ticket_count = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='입금 판매 매수',
        help_text='예매처별(입금) 판매 매수'
    )
    paid_by_grade = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='입금 등급별 판매 매수',
        help_text='예매처별(입금) 등급별 판매 매수 (예: {"VIP": 5, "R석": 10})'
    )
    
    # 유료 - 미입금
    unpaid_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name='미입금 판매액 (원)',
        help_text='예매처별(미입금) 판매액'
    )
    unpaid_ticket_count = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name='미입금 판매 매수',
        help_text='예매처별(미입금) 판매 매수'
    )
    unpaid_by_grade = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='미입금 등급별 판매 매수',
        help_text='예매처별(미입금) 등급별 판매 매수 (예: {"VIP": 2, "R석": 3})'
    )
    
    # 무료
    free_by_grade = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='등급별 초대 매수',
        help_text='예매처별 등급별 초대 매수 (예: {"VIP": 1, "R석": 2})'
    )
    
    notes = models.TextField(blank=True, verbose_name='비고')
    
    # 메타 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        verbose_name = '콘서트 데일리 매출'
        verbose_name_plural = '콘서트 데일리 매출'
        ordering = ['-date', 'performance', 'booking_site']
        indexes = [
            models.Index(fields=['performance', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['booking_site']),
        ]
        # 같은 공연, 같은 날짜, 같은 예매처는 중복 방지
        unique_together = [['performance', 'date', 'booking_site']]
    
    def __str__(self):
        return f'{self.performance.title} - {self.date} - {self.booking_site}'
    
    def get_total_revenue(self):
        """총 매출액 계산 (입금 + 미입금)"""
        return self.paid_revenue + self.unpaid_revenue
    
    def get_total_ticket_count(self):
        """총 판매 매수 계산 (입금 + 미입금)"""
        return self.paid_ticket_count + self.unpaid_ticket_count


class ConcertFinalSales(models.Model):
    """콘서트 최종 매출 모델"""
    
    performance = models.ForeignKey(
        'performance.Performance',
        on_delete=models.CASCADE,
        limit_choices_to={'genre': 'concert'},
        verbose_name='공연',
        related_name='final_sales'
    )
    booking_site = models.CharField(max_length=100, verbose_name='예매처')
    
    # 유료 - 입금
    paid_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='입금 판매액 (원)',
        help_text='예매처별(입금) 판매액'
    )
    paid_ticket_count = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='입금 판매 매수',
        help_text='예매처별(입금) 판매 매수'
    )
    paid_by_grade = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='입금 등급별 판매 매수',
        help_text='예매처별(입금) 등급별 판매 매수 (예: {"VIP": 5, "R석": 10})'
    )
    
    # 유료 - 미입금
    unpaid_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name='미입금 판매액 (원)',
        help_text='예매처별(미입금) 판매액'
    )
    unpaid_ticket_count = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name='미입금 판매 매수',
        help_text='예매처별(미입금) 판매 매수'
    )
    unpaid_by_grade = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='미입금 등급별 판매 매수',
        help_text='예매처별(미입금) 등급별 판매 매수 (예: {"VIP": 2, "R석": 3})'
    )
    
    # 무료
    free_by_grade = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='등급별 초대 매수',
        help_text='예매처별 등급별 초대 매수 (예: {"VIP": 1, "R석": 2})'
    )
    
    # 최종 매출 상세 정보
    grade_sales_summary = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='예매처 통합 등급별 판매현황',
        help_text='관람 등급별 판매 정보 (예: {"VIP": {"paid_count": 100, "free_count": 10, "revenue": 15000000, "paid_occupancy_rate": 0.85, "total_occupancy_rate": 0.92, "total_count": 110}})'
    )
    booking_site_discount_sales = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='예매처별 할인권종별 판매현황',
        help_text='예매처별 할인권종별 판매 정보 (예: {"인터파크": [{"discount_type": "조조할인", "sales_count": 50, "revenue": 5000000}]})'
    )
    age_gender_sales = models.JSONField(
        default=list,
        blank=True,
        verbose_name='연령대별 성별 판매현황',
        help_text='연령대별, 성별별 판매 매수 (예: [{"age_group": "21 ~ 30", "male_count": 100, "female_count": 120, "unknown_count": 10, "total_count": 230}])'
    )
    payment_method_sales = models.JSONField(
        default=list,
        blank=True,
        verbose_name='결제수단별 판매현황',
        help_text='결제수단별 매수 및 금액 (예: [{"payment_method": "신용카드", "count": 500, "amount": 50000000}])'
    )
    card_sales_summary = models.JSONField(
        default=list,
        blank=True,
        verbose_name='카드별 매출집계',
        help_text='카드 종류별 매수 및 금액 (예: [{"card_type": "삼성카드", "count": 200, "amount": 20000000}])'
    )
    sales_channel_sales = models.JSONField(
        default=list,
        blank=True,
        verbose_name='판매경로별 판매현황',
        help_text='판매경로별 매수 및 금액 (예: [{"sales_channel": "온라인", "count": 600, "amount": 60000000}])'
    )
    region_sales = models.JSONField(
        default=list,
        blank=True,
        verbose_name='지역별 판매현황',
        help_text='지역별 매수 (예: [{"region": "서울", "count": 400}])'
    )
    seoul_region_sales = models.JSONField(
        default=list,
        blank=True,
        verbose_name='서울 지역별 판매현황',
        help_text='서울 지역별 매수 (예: [{"region": "강남구", "count": 100}])'
    )
    gyeonggi_region_sales = models.JSONField(
        default=list,
        blank=True,
        verbose_name='경기 지역별 판매현황',
        help_text='경기 지역별 매수 (예: [{"region": "수원시", "count": 50}])'
    )
    
    notes = models.TextField(blank=True, verbose_name='비고')
    
    # 메타 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        verbose_name = '콘서트 최종 매출'
        verbose_name_plural = '콘서트 최종 매출'
        ordering = ['performance', 'booking_site']
        indexes = [
            models.Index(fields=['performance']),
            models.Index(fields=['booking_site']),
        ]
        # 같은 공연, 같은 예매처는 중복 방지 (예매처별로 하나만)
        unique_together = [['performance', 'booking_site']]
    
    def __str__(self):
        return f'{self.performance.title} - 최종 - {self.booking_site}'
    
    def get_total_revenue(self):
        """총 매출액 계산 (입금 + 미입금)"""
        return self.paid_revenue + self.unpaid_revenue
    
    def get_total_ticket_count(self):
        """총 판매 매수 계산 (입금 + 미입금)"""
        return self.paid_ticket_count + self.unpaid_ticket_count
