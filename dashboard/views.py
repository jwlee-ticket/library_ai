from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.db.models import Q
from performance.models import Performance


@login_required
def main_view(request):
    """통합 대시보드 메인 뷰"""
    # 통합 대시보드 메인 페이지 (추후 구현 예정)
    return render(request, 'dashboard/main.html')


class PerformanceDashboardListView(ListView):
    """공연별 대시보드 리스트 뷰"""
    model = Performance
    template_name = 'dashboard/list.html'
    context_object_name = 'performances'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Performance.objects.all()
        
        # 장르 필터
        genre = self.request.GET.get('genre')
        if genre:
            queryset = queryset.filter(genre=genre)
        
        # 검색
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(title_en__icontains=search) |
                Q(venue__icontains=search) |
                Q(producer__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre_filter'] = self.request.GET.get('genre', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['genre_choices'] = Performance.GENRE_CHOICES
        return context


class PerformanceDashboardDetailView(DetailView):
    """공연별 대시보드 상세 뷰 (임시 - 추후 구현 예정)"""
    model = Performance
    template_name = 'dashboard/detail.html'
    context_object_name = 'performance'
