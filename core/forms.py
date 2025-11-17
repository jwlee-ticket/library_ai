from django import forms
from django.contrib.auth.forms import AuthenticationForm


class EmailAuthenticationForm(AuthenticationForm):
    """이메일 기반 로그인 폼"""
    username = forms.EmailField(
        label='이메일',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': '이메일을 입력하세요',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-colors',
            'placeholder': '비밀번호를 입력하세요',
        })
    )
    
    error_messages = {
        'invalid_login': '이메일 또는 비밀번호가 올바르지 않습니다.',
        'inactive': '이 계정은 비활성화되어 있습니다.',
    }

