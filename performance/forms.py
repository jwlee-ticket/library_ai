from django import forms
from django.forms import inlineformset_factory
import json
from .models import Performance, SeatGrade, BookingSite, DiscountType, Person, CastingRole


class PerformanceForm(forms.ModelForm):
    """공연 폼"""
    
    class Meta:
        model = Performance
        fields = [
            'title',
            'title_en',
            'genre',
            'venue',
            'postcode',
            'address',
            'performance_start',
            'performance_end',
            'sales_start',
            'sales_end',
            'age_rating',
            'running_time',
            'description',
            'producer',
            'organizer',
            'target_revenue',
            'break_even_point',
            'total_production_cost',
            'seat_map',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '공연명을 입력해주세요',
            }),
            'title_en': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '공연명(영문)을 입력해주세요',
            }),
            'genre': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'venue': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '공연장을 입력해주세요',
            }),
            'postcode': forms.HiddenInput(),
            'address': forms.TextInput(attrs={
                'class': 'flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors bg-gray-50',
                'placeholder': '공연장 주소',
                'readonly': True,
            }),
            'performance_start': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'performance_end': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'sales_start': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'sales_end': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'age_rating': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '예: 만 12세 이상',
            }),
            'running_time': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '예: 150분 (인터미션 포함)',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'rows': 5,
                'placeholder': '공연 설명을 입력해주세요',
            }),
            'producer': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '제작/주최를 입력해주세요',
            }),
            'organizer': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '주관을 입력해주세요',
            }),
            'target_revenue': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
                'step': '1',
            }),
            'break_even_point': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
                'step': '1',
            }),
            'total_production_cost': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '0',
                'min': '0',
                'step': '1',
            }),
            'seat_map': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'accept': 'image/*',
            }),
        }


# 인라인 폼셋 클래스 생성
SeatGradeFormSet = inlineformset_factory(
    Performance,
    SeatGrade,
    fields=['name', 'price', 'seat_count', 'order'],
    extra=1,
    can_delete=True,
    widgets={
        'name': forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': '등급명',
        }),
        'price': forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': '티켓 가격',
            'min': '0',
            'step': '1',
        }),
        'seat_count': forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': '좌석 수',
            'min': '0',
            'step': '1',
        }),
        'order': forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': '0',
            'min': '0',
            'step': '1',
        }),
    }
)


BookingSiteFormSet = inlineformset_factory(
    Performance,
    BookingSite,
    fields=['name', 'url'],
    extra=1,
    can_delete=True,
    widgets={
        'name': forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': '예매처명',
        }),
        'url': forms.URLInput(attrs={
            'class': 'w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': 'https://...',
        }),
    }
)


class DiscountTypeForm(forms.ModelForm):
    """할인권종 폼 (좌석 등급 이름 매핑용 숨은 필드 포함)"""

    applicable_grade_names = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text='선택된 좌석 등급 이름 목록 (JSON)'
    )

    class Meta:
        model = DiscountType
        fields = ['name', 'start_date', 'end_date', 'discount_rate', 'applicable_grades']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '할인권종명',
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
            'discount_rate': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'placeholder': '할인율',
                'min': '0',
                'max': '100',
                'step': '1',
            }),
            'applicable_grades': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            }),
        }

    def clean_applicable_grade_names(self):
        raw_value = self.cleaned_data.get('applicable_grade_names') or '[]'
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError:
            return []
        if not isinstance(parsed, list):
            return []
        return [str(name).strip() for name in parsed if str(name).strip()]


DiscountTypeFormSet = inlineformset_factory(
    Performance,
    DiscountType,
    form=DiscountTypeForm,
    extra=1,
    can_delete=True,
)


CastingRoleFormSet = inlineformset_factory(
    Performance,
    CastingRole,
    fields=['person', 'role', 'order'],
    extra=1,
    can_delete=True,
    widgets={
        'person': forms.Select(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
        }),
        'role': forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': '역할명',
        }),
        'order': forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': '0',
            'min': '0',
            'step': '1',
        }),
    }
)

