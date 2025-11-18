from django import forms
from .models import Performance


class PerformanceForm(forms.ModelForm):
    """공연 폼"""
    
    class Meta:
        model = Performance
        fields = [
            'title',
            'title_en',
            'genre',
            'venue',
            'performance_start',
            'performance_end',
            'sales_start',
            'sales_end',
            'age_rating',
            'running_time',
            'description',
            'producer',
            'organizer',
            'seat_grades',
            'crew',
            'booking_sites',
            'ticket_prices',
            'seat_counts',
            'discounts',
            'casting',
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
            'seat_grades': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'rows': 3,
                'placeholder': 'JSON 형식: ["VIP", "R석", "S석"]',
            }),
            'crew': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'rows': 3,
                'placeholder': 'JSON 형식: ["감독: 홍길동", "음악: 김철수"]',
            }),
            'booking_sites': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'rows': 3,
                'placeholder': 'JSON 형식: [{"인터파크": "https://..."}, {"예스24": "https://..."}]',
            }),
            'ticket_prices': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'rows': 3,
                'placeholder': 'JSON 형식: {"VIP": 150000, "R석": 100000}',
            }),
            'seat_counts': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'rows': 3,
                'placeholder': 'JSON 형식: {"VIP": 50, "R석": 200}',
            }),
            'discounts': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'rows': 3,
                'placeholder': 'JSON 형식: {"VIP": {"조조할인": 10, "단체할인": 15}}',
            }),
            'casting': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'rows': 3,
                'placeholder': 'JSON 형식: {"홍길동": "배우A", "김철수": "배우B"}',
            }),
            'seat_map': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
                'accept': 'image/*',
            }),
        }
    
    def clean_seat_grades(self):
        """좌석 등급 JSON 검증"""
        data = self.cleaned_data.get('seat_grades')
        if data:
            try:
                import json
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, list):
                    raise forms.ValidationError('리스트 형식이어야 해요')
            except json.JSONDecodeError:
                raise forms.ValidationError('올바른 JSON 형식이 아니에요')
        return data
    
    def clean_crew(self):
        """제작진 JSON 검증"""
        data = self.cleaned_data.get('crew')
        if data:
            try:
                import json
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, list):
                    raise forms.ValidationError('리스트 형식이어야 해요')
            except json.JSONDecodeError:
                raise forms.ValidationError('올바른 JSON 형식이 아니에요')
        return data
    
    def clean_booking_sites(self):
        """예매처 JSON 검증"""
        data = self.cleaned_data.get('booking_sites')
        if data:
            try:
                import json
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, list):
                    raise forms.ValidationError('리스트 형식이어야 해요')
            except json.JSONDecodeError:
                raise forms.ValidationError('올바른 JSON 형식이 아니에요')
        return data
    
    def clean_ticket_prices(self):
        """티켓 가격 JSON 검증"""
        data = self.cleaned_data.get('ticket_prices')
        if data:
            try:
                import json
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, dict):
                    raise forms.ValidationError('딕셔너리 형식이어야 해요')
            except json.JSONDecodeError:
                raise forms.ValidationError('올바른 JSON 형식이 아니에요')
        return data
    
    def clean_seat_counts(self):
        """좌석 수 JSON 검증"""
        data = self.cleaned_data.get('seat_counts')
        if data:
            try:
                import json
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, dict):
                    raise forms.ValidationError('딕셔너리 형식이어야 해요')
            except json.JSONDecodeError:
                raise forms.ValidationError('올바른 JSON 형식이 아니에요')
        return data
    
    def clean_discounts(self):
        """할인율 JSON 검증"""
        data = self.cleaned_data.get('discounts')
        if data:
            try:
                import json
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, dict):
                    raise forms.ValidationError('딕셔너리 형식이어야 해요')
            except json.JSONDecodeError:
                raise forms.ValidationError('올바른 JSON 형식이 아니에요')
        return data
    
    def clean_casting(self):
        """캐스팅 JSON 검증"""
        data = self.cleaned_data.get('casting')
        if data:
            try:
                import json
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, dict):
                    raise forms.ValidationError('딕셔너리 형식이어야 해요')
            except json.JSONDecodeError:
                raise forms.ValidationError('올바른 JSON 형식이 아니에요')
        return data

