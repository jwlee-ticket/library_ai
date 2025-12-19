from django.db import models
from django.core.validators import MinValueValidator


class Person(models.Model):
    """인물 모델 (감독, 배우, 제작진 등 통합 관리)"""
    
    name = models.CharField(max_length=200, verbose_name='이름', help_text='인물 이름')
    name_en = models.CharField(max_length=200, blank=True, verbose_name='이름(영문)', help_text='인물 이름 영문')
    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
        related_name='persons',
        verbose_name='회사',
        help_text='인물이 소속된 회사'
    )
    
    # 메타 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        verbose_name = '인물'
        verbose_name_plural = '인물들'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['company']),
        ]
    
    def __str__(self):
        return self.name


class SeatGrade(models.Model):
    """좌석 등급 모델"""
    
    performance = models.ForeignKey(
        'Performance',
        on_delete=models.CASCADE,
        related_name='seat_grades',
        verbose_name='공연'
    )
    name = models.CharField(max_length=50, verbose_name='등급명', help_text='예: VIP, R석, S석')
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='티켓 가격 (원)',
        help_text='해당 등급의 티켓 가격'
    )
    seat_count = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='좌석 수',
        help_text='해당 등급의 총 좌석 수'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='정렬 순서',
        help_text='등급 표시 순서 (작을수록 먼저 표시)'
    )
    
    class Meta:
        verbose_name = '좌석 등급'
        verbose_name_plural = '좌석 등급들'
        ordering = ['performance', 'order', 'name']
        indexes = [
            models.Index(fields=['performance', 'order']),
        ]
        unique_together = [['performance', 'name']]
    
    def __str__(self):
        return f'{self.performance.title} - {self.name}'


class BookingSite(models.Model):
    """예매처 모델"""
    
    performance = models.ForeignKey(
        'Performance',
        on_delete=models.CASCADE,
        related_name='booking_sites',
        verbose_name='공연'
    )
    name = models.CharField(max_length=100, verbose_name='예매처명', help_text='예: 인터파크, 예스24')
    url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='예매 URL',
        help_text='해당 예매처의 예매 페이지 URL'
    )
    
    class Meta:
        verbose_name = '예매처'
        verbose_name_plural = '예매처들'
        ordering = ['performance', 'name']
        indexes = [
            models.Index(fields=['performance', 'name']),
        ]
        unique_together = [['performance', 'name']]
    
    def __str__(self):
        return f'{self.performance.title} - {self.name}'


class DiscountType(models.Model):
    """할인권종 모델"""
    
    performance = models.ForeignKey(
        'Performance',
        on_delete=models.CASCADE,
        related_name='discount_types',
        verbose_name='공연'
    )
    name = models.CharField(max_length=100, verbose_name='할인권종명', help_text='예: 조조할인, 조기예매할인')
    start_date = models.DateField(verbose_name='할인 시작일')
    end_date = models.DateField(verbose_name='할인 종료일')
    discount_rate = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='할인율 (%)',
        help_text='할인 비율 (예: 10 = 10% 할인)'
    )
    applicable_grades = models.ManyToManyField(
        'SeatGrade',
        related_name='applicable_discount_types',
        blank=True,
        verbose_name='적용 가능한 등급',
        help_text='이 할인을 적용할 수 있는 좌석 등급들'
    )
    
    class Meta:
        verbose_name = '할인권종'
        verbose_name_plural = '할인권종들'
        ordering = ['performance', 'start_date', 'name']
        indexes = [
            models.Index(fields=['performance', 'start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f'{self.performance.title} - {self.name}'


class CrewRole(models.Model):
    """제작진 역할 모델"""
    
    performance = models.ForeignKey(
        'Performance',
        on_delete=models.CASCADE,
        related_name='crew_roles',
        verbose_name='공연'
    )
    person = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
        verbose_name='인물',
        help_text='제작진 인물'
    )
    role = models.CharField(max_length=100, verbose_name='역할', help_text='예: 감독, 음악, 작사, 작곡 등')
    order = models.IntegerField(
        default=0,
        verbose_name='정렬 순서',
        help_text='역할 표시 순서 (작을수록 먼저 표시)'
    )
    
    class Meta:
        verbose_name = '제작진 역할'
        verbose_name_plural = '제작진 역할들'
        ordering = ['performance', 'order', 'role']
        indexes = [
            models.Index(fields=['performance', 'order']),
            models.Index(fields=['person']),
        ]
        unique_together = [['performance', 'person', 'role']]
    
    def __str__(self):
        return f'{self.performance.title} - {self.role}: {self.person.name}'


class CastingRole(models.Model):
    """캐스팅 역할 모델"""
    
    performance = models.ForeignKey(
        'Performance',
        on_delete=models.CASCADE,
        related_name='casting_roles',
        verbose_name='공연'
    )
    person = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
        verbose_name='인물',
        help_text='배우 인물'
    )
    role = models.CharField(max_length=100, verbose_name='역할', help_text='예: 홍길동, 김철수 등 배역명')
    order = models.IntegerField(
        default=0,
        verbose_name='정렬 순서',
        help_text='역할 표시 순서 (작을수록 먼저 표시)'
    )
    
    class Meta:
        verbose_name = '캐스팅 역할'
        verbose_name_plural = '캐스팅 역할들'
        ordering = ['performance', 'order', 'role']
        indexes = [
            models.Index(fields=['performance', 'order']),
            models.Index(fields=['person']),
        ]
        unique_together = [['performance', 'person', 'role']]
    
    def __str__(self):
        return f'{self.performance.title} - {self.role}: {self.person.name}'


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
    
    # 주소 필드 (카카오 우편번호 API 사용)
    postcode = models.CharField(max_length=10, blank=True, verbose_name='우편번호')
    address = models.CharField(max_length=200, verbose_name='공연장 주소')
    
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
    
    # 이미지 필드
    seat_map = models.ImageField(
        upload_to='seat_maps/',
        null=True,
        blank=True,
        verbose_name='좌석배치도'
    )
    
    # 회사 필드
    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
        related_name='performances',
        verbose_name='회사',
        help_text='공연을 소유한 회사'
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
            models.Index(fields=['company']),
        ]
    
    def __str__(self):
        return self.title
