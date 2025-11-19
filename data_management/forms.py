from django import forms
from django.core.exceptions import ValidationError
from .models import ConcertSales
from performance.models import Performance
import json


class ConcertSalesForm(forms.ModelForm):
    """콘서트 매출 폼"""
    
    class Meta:
        model = ConcertSales
        fields = [
            'performance',
            'date',
            'booking_site',
            'paid_revenue',
            'paid_ticket_count',
            'paid_by_grade',
            'unpaid_revenue',
            'unpaid_ticket_count',
            'unpaid_by_grade',
            'free_by_grade',
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
            'booking_site': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '예매처를 입력하세요',
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
            'paid_by_grade': forms.HiddenInput(),
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
            'unpaid_by_grade': forms.HiddenInput(),
            'free_by_grade': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'rows': 3,
                'placeholder': '비고를 입력하세요',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 콘서트 공연만 필터링
        self.fields['performance'].queryset = Performance.objects.filter(genre='concert')
        self.fields['performance'].label = '공연'
        self.fields['performance'].empty_label = '공연을 선택하세요'
    
    def clean_paid_by_grade(self):
        """입금 등급별 매수 JSON 검증"""
        data = self.cleaned_data.get('paid_by_grade')
        if data:
            try:
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, dict):
                    raise forms.ValidationError('딕셔너리 형식이어야 해요')
                # 값이 모두 숫자인지 확인
                for key, value in data.items():
                    if not isinstance(value, (int, float)) or value < 0:
                        raise forms.ValidationError('등급별 매수는 0 이상의 숫자여야 해요')
            except json.JSONDecodeError:
                raise forms.ValidationError('올바른 JSON 형식이 아니에요')
        return data
    
    def clean_unpaid_by_grade(self):
        """미입금 등급별 매수 JSON 검증"""
        data = self.cleaned_data.get('unpaid_by_grade')
        if data:
            try:
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, dict):
                    raise forms.ValidationError('딕셔너리 형식이어야 해요')
                # 값이 모두 숫자인지 확인
                for key, value in data.items():
                    if not isinstance(value, (int, float)) or value < 0:
                        raise forms.ValidationError('등급별 매수는 0 이상의 숫자여야 해요')
            except json.JSONDecodeError:
                raise forms.ValidationError('올바른 JSON 형식이 아니에요')
        return data
    
    def clean_free_by_grade(self):
        """무료 등급별 매수 JSON 검증"""
        data = self.cleaned_data.get('free_by_grade')
        if data:
            try:
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, dict):
                    raise forms.ValidationError('딕셔너리 형식이어야 해요')
                # 값이 모두 숫자인지 확인
                for key, value in data.items():
                    if not isinstance(value, (int, float)) or value < 0:
                        raise forms.ValidationError('등급별 매수는 0 이상의 숫자여야 해요')
            except json.JSONDecodeError:
                raise forms.ValidationError('올바른 JSON 형식이 아니에요')
        return data
    
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
            booking_sites = performance.booking_sites
            if booking_sites:
                # booking_sites는 [{"인터파크": "https://..."}, ...] 형태
                valid_sites = []
                for site_dict in booking_sites:
                    if isinstance(site_dict, dict):
                        valid_sites.extend(site_dict.keys())
                
                if valid_sites and booking_site not in valid_sites:
                    raise ValidationError({
                        'booking_site': f'등록된 예매처({", ".join(valid_sites)}) 중에서 선택해주세요'
                    })
        
        # 등급별 매수 합계 검증 (경고만, 강제는 아님)
        paid_by_grade = cleaned_data.get('paid_by_grade', {})
        paid_ticket_count = cleaned_data.get('paid_ticket_count', 0)
        
        if paid_by_grade and isinstance(paid_by_grade, dict):
            grade_sum = sum(int(v) for v in paid_by_grade.values() if isinstance(v, (int, float)))
            if grade_sum > 0 and paid_ticket_count > 0 and grade_sum != paid_ticket_count:
                # 경고만 표시 (필드에 에러 추가하지 않음)
                pass  # 템플릿에서 JavaScript로 경고 표시
        
        unpaid_by_grade = cleaned_data.get('unpaid_by_grade', {})
        unpaid_ticket_count = cleaned_data.get('unpaid_ticket_count', 0)
        
        if unpaid_by_grade and isinstance(unpaid_by_grade, dict):
            grade_sum = sum(int(v) for v in unpaid_by_grade.values() if isinstance(v, (int, float)))
            if grade_sum > 0 and unpaid_ticket_count > 0 and grade_sum != unpaid_ticket_count:
                # 경고만 표시
                pass
        
        return cleaned_data

