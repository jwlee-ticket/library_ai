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
            'seat_grades',
            'crew',
            'booking_sites',
            'ticket_prices',
            'seat_counts',
            'discount_types',
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
            'seat_grades': forms.HiddenInput(),
            'crew': forms.HiddenInput(),
            'booking_sites': forms.HiddenInput(),
            'ticket_prices': forms.HiddenInput(),
            'seat_counts': forms.HiddenInput(),
            'discount_types': forms.HiddenInput(),
            'casting': forms.HiddenInput(),
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
        else:
            # 빈 문자열이나 None인 경우 빈 리스트로 처리
            data = []
        
        # 최소 1개 이상 필수
        if not data or len(data) == 0:
            raise forms.ValidationError('좌석 등급을 최소 1개 이상 입력해주세요')
        
        return data
    
    def clean_crew(self):
        """제작진 JSON 검증"""
        data = self.cleaned_data.get('crew')
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
    
    def clean_discount_types(self):
        """할인권종 JSON 검증"""
        data = self.cleaned_data.get('discount_types')
        if data:
            try:
                import json
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, list):
                    raise forms.ValidationError('리스트 형식이어야 해요')
                
                # seat_grades 가져오기
                seat_grades = self.cleaned_data.get('seat_grades', [])
                if isinstance(seat_grades, str):
                    seat_grades = json.loads(seat_grades) if seat_grades else []
                
                # 각 항목 검증
                for item in data:
                    if not isinstance(item, dict):
                        raise forms.ValidationError('각 항목은 딕셔너리 형식이어야 해요')
                    required_fields = ['name', 'start_date', 'end_date', 'grade', 'discount_rate']
                    for field in required_fields:
                        if field not in item:
                            raise forms.ValidationError(f'{field} 필드가 필요해요')
                    
                    # 등급이 seat_grades에 있는지 검증
                    grade = item.get('grade', '').strip()
                    if grade and seat_grades and grade not in seat_grades:
                        raise forms.ValidationError(f'등급 "{grade}"는 생성된 좌석 등급에 없어요. 먼저 좌석 등급을 추가해주세요.')
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

