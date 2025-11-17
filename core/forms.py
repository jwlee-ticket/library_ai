from django import forms
from django.contrib.auth.forms import AuthenticationForm


class EmailAuthenticationForm(AuthenticationForm):
    """이메일 기반 로그인 폼"""
    username = forms.EmailField(
        label='이메일',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500',
            'placeholder': '이메일을 입력하세요',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500',
            'placeholder': '비밀번호를 입력하세요',
        })
    )
    
    error_messages = {
        'invalid_login': '이메일 또는 비밀번호가 올바르지 않습니다.',
        'inactive': '이 계정은 비활성화되어 있습니다.',
    }

