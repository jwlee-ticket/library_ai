from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import EmailAuthenticationForm


class CustomLoginView(LoginView):
    """커스텀 로그인 뷰"""
    form_class = EmailAuthenticationForm
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # settings.py의 LOGIN_REDIRECT_URL 사용 (현재는 '/')
        # dashboard URL 설정 후 변경 필요
        return super().get_success_url()


@login_required
def logout_view(request):
    """로그아웃 뷰"""
    logout(request)
    return redirect('core:login')
