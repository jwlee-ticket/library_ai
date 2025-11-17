from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def main_view(request):
    """통합 대시보드 메인 뷰"""
    return render(request, 'dashboard/main.html')
