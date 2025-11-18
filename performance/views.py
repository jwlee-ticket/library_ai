from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Performance
from .forms import PerformanceForm


class PerformanceListView(ListView):
    """공연 목록 뷰"""
    model = Performance
    template_name = 'performance/list.html'
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


class PerformanceDetailView(DetailView):
    """공연 상세 뷰"""
    model = Performance
    template_name = 'performance/detail.html'
    context_object_name = 'performance'


class PerformanceCreateView(CreateView):
    """공연 생성 뷰"""
    model = Performance
    form_class = PerformanceForm
    template_name = 'performance/form.html'
    success_url = reverse_lazy('performance:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre_choices'] = Performance.GENRE_CHOICES
        if self.object:
            context['genre_filter'] = self.object.genre
        else:
            context['genre_filter'] = ''
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '공연이 성공적으로 등록되었어요')
        return super().form_valid(form)


class PerformanceUpdateView(UpdateView):
    """공연 수정 뷰"""
    model = Performance
    form_class = PerformanceForm
    template_name = 'performance/form.html'
    success_url = reverse_lazy('performance:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre_choices'] = Performance.GENRE_CHOICES
        if self.object:
            context['genre_filter'] = self.object.genre
        else:
            context['genre_filter'] = ''
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '공연 정보가 성공적으로 수정되었어요')
        return super().form_valid(form)


class PerformanceDeleteView(DeleteView):
    """공연 삭제 뷰"""
    model = Performance
    template_name = 'performance/confirm_delete.html'
    success_url = reverse_lazy('performance:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '공연이 성공적으로 삭제되었어요')
        return super().delete(request, *args, **kwargs)
