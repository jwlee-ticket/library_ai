from django import forms
from django.forms import modelformset_factory
from django.core.exceptions import ValidationError
from .models import PerformanceDailySales, PerformanceFinalSales
from performance.models import Performance
import json


class PerformanceDailySalesForm(forms.ModelForm):
    """공연 데일리 매출 폼"""
    
    class Meta:
        model = PerformanceDailySales
        fields = [
            'performance',
            'date',
            'booking_site',
            'paid_revenue',
            'paid_ticket_count',
            'unpaid_revenue',
            'unpaid_ticket_count',
            'notes',
        ]
        widgets = {
            'performance': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'booking_site': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'paid_revenue': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
            }),
            'paid_ticket_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
            }),
            'unpaid_revenue': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
            }),
            'unpaid_ticket_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'rows': 3,
                'placeholder': '비고를 입력하세요',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 모든 공연 선택 가능
        self.fields['performance'].queryset = Performance.objects.all()
        self.fields['performance'].label = '공연'
        self.fields['performance'].empty_label = '공연을 선택하세요'
        
        # 예매처 필드 동적 설정
        performance_id = None
        if self.instance and self.instance.pk:
            performance_id = self.instance.performance_id
        elif 'performance' in self.initial:
            performance_id = self.initial['performance']
        
        if performance_id:
            try:
                performance = Performance.objects.get(id=performance_id)
                self.fields['booking_site'].queryset = performance.booking_sites.all()
                self.fields['booking_site'].empty_label = '예매처를 선택하세요'
            except Performance.DoesNotExist:
                self.fields['booking_site'].queryset = Performance.objects.none()
        else:
            self.fields['booking_site'].queryset = Performance.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        performance = cleaned_data.get('performance')
        date = cleaned_data.get('date')
        booking_site = cleaned_data.get('booking_site')
        
        # 공연 기간 검증
        if performance and date:
            if date < performance.performance_start or date > performance.performance_end:
                raise ValidationError({
                    'date': f'공연 기간({performance.performance_start} ~ {performance.performance_end}) 내의 날짜를 선택해주세요'
                })
        
        # 예매처 검증 (Performance의 booking_sites에 있는지 확인)
        if performance and booking_site:
            booking_sites = performance.booking_sites.all()
            if booking_sites:
                valid_site_ids = [site.id for site in booking_sites]
                if booking_site.id not in valid_site_ids:
                    valid_site_names = [site.name for site in booking_sites]
                    raise ValidationError({
                        'booking_site': f'등록된 예매처({", ".join(valid_site_names)}) 중에서 선택해주세요'
                    })
        
        return cleaned_data


class PerformanceFinalSalesForm(forms.ModelForm):
    """공연 최종 매출 폼"""
    
    class Meta:
        model = PerformanceFinalSales
        fields = [
            'performance',
            'booking_site',
            'paid_revenue',
            'paid_ticket_count',
            'unpaid_revenue',
            'unpaid_ticket_count',
            'notes',
        ]
        widgets = {
            'performance': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'booking_site': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'paid_revenue': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
            }),
            'paid_ticket_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
            }),
            'unpaid_revenue': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
            }),
            'unpaid_ticket_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'rows': 3,
                'placeholder': '비고를 입력하세요',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 모든 공연 선택 가능
        self.fields['performance'].queryset = Performance.objects.all()
        self.fields['performance'].label = '공연'
        self.fields['performance'].empty_label = '공연을 선택하세요'
        
        # 예매처 필드 동적 설정
        performance_id = None
        if self.instance and self.instance.pk:
            performance_id = self.instance.performance_id
        elif 'performance' in self.initial:
            performance_id = self.initial['performance']
        
        if performance_id:
            try:
                performance = Performance.objects.get(id=performance_id)
                self.fields['booking_site'].queryset = performance.booking_sites.all()
                self.fields['booking_site'].empty_label = '예매처를 선택하세요'
            except Performance.DoesNotExist:
                self.fields['booking_site'].queryset = Performance.objects.none()
        else:
            self.fields['booking_site'].queryset = Performance.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        performance = cleaned_data.get('performance')
        booking_site = cleaned_data.get('booking_site')
        
        # 예매처 검증 (Performance의 booking_sites에 있는지 확인)
        if performance and booking_site:
            booking_sites = performance.booking_sites.all()
            if booking_sites:
                valid_site_ids = [site.id for site in booking_sites]
                if booking_site.id not in valid_site_ids:
                    valid_site_names = [site.name for site in booking_sites]
                    raise ValidationError({
                        'booking_site': f'등록된 예매처({", ".join(valid_site_names)}) 중에서 선택해주세요'
                    })
        
        return cleaned_data


class PerformanceSalesDailyForm(forms.ModelForm):
    """데일리 매출 입력용 폼 (등급별 필드 동적 생성)"""
    
    class Meta:
        model = PerformanceDailySales
        fields = [
            'performance',
            'date',
            'booking_site',
            'paid_revenue',
            'paid_ticket_count',
            'unpaid_revenue',
            'unpaid_ticket_count',
        ]
        widgets = {
            'performance': forms.HiddenInput(),
            'date': forms.HiddenInput(),
            'booking_site': forms.HiddenInput(),
            'paid_revenue': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
                'step': '1',
            }),
            'paid_ticket_count': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
                'step': '1',
            }),
            'unpaid_revenue': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
                'step': '1',
            }),
            'unpaid_ticket_count': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
                'step': '1',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.seat_grades = kwargs.pop('seat_grades', [])
        super().__init__(*args, **kwargs)
        
        # 등급별 입력 필드 동적 생성
        if self.seat_grades:
            for grade in self.seat_grades:
                # 입금 등급별 매수
                self.fields[f'paid_grade_{grade}'] = forms.IntegerField(
                    required=False,
                    min_value=0,
                    widget=forms.NumberInput(attrs={
                        'class': 'w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                        'placeholder': '0',
                        'min': '0',
                        'step': '1',
                    })
                )
                # 미입금 등급별 매수
                self.fields[f'unpaid_grade_{grade}'] = forms.IntegerField(
                    required=False,
                    min_value=0,
                    widget=forms.NumberInput(attrs={
                        'class': 'w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                        'placeholder': '0',
                        'min': '0',
                        'step': '1',
                    })
                )
                # 무료 등급별 매수
                self.fields[f'free_grade_{grade}'] = forms.IntegerField(
                    required=False,
                    min_value=0,
                    widget=forms.NumberInput(attrs={
                        'class': 'w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                        'placeholder': '0',
                        'min': '0',
                        'step': '1',
                    })
                )
    
    def clean(self):
        cleaned_data = super().clean()
        # 등급별 매수는 나중에 PerformanceDailySalesGrade 모델로 저장됨
        # 여기서는 폼 데이터만 정리
        return cleaned_data


# 날짜별 Formset 생성
PerformanceSalesDailyFormSet = modelformset_factory(
    PerformanceDailySales,
    form=PerformanceSalesDailyForm,
    extra=0,
    can_delete=False,
)

