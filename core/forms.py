from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


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
    
    def clean(self):
        """이메일을 username으로 변환하여 인증"""
        email = self.cleaned_data.get('username')  # 폼에서는 username 필드에 이메일 입력
        password = self.cleaned_data.get('password')
        
        if email and password:
            # 이메일로 사용자 찾기
            try:
                user = User.objects.get(email=email)
                # username을 실제 username으로 설정
                self.cleaned_data['username'] = user.username
            except User.DoesNotExist:
                # 사용자가 없으면 기본 인증 로직에서 처리하도록
                pass
            
            # 부모 클래스의 clean() 호출하여 인증 수행
            return super().clean()
        
        return self.cleaned_data

