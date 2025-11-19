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
