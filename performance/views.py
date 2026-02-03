from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Q
from .models import Performance, SeatGrade
from .forms import PerformanceForm, SeatGradeFormSet, BookingSiteFormSet, DiscountTypeFormSet


def sync_discount_type_grades(performance, discount_type_formset):
    """할인권종의 적용 가능한 등급을 이름 기준으로 동기화"""
    seat_grades = SeatGrade.objects.filter(performance=performance)
    for form in discount_type_formset.forms:
        if not form.cleaned_data or form.cleaned_data.get('DELETE'):
            continue
        grade_names = form.cleaned_data.get('applicable_grade_names', [])
        if grade_names is None:
            continue
        matched_grades = seat_grades.filter(name__in=grade_names)
        if form.instance.pk:
            form.instance.applicable_grades.set(matched_grades)


class PerformanceListView(LoginRequiredMixin, ListView):
    """공연 목록 뷰"""
    model = Performance
    template_name = 'performance/list.html'
    context_object_name = 'performances'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
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


class PerformanceDetailView(LoginRequiredMixin, DetailView):
    """공연 상세 뷰"""
    model = Performance
    template_name = 'performance/detail.html'
    context_object_name = 'performance'


class PerformanceCreateView(LoginRequiredMixin, CreateView):
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
            # 인라인 폼셋 초기화
            context['seat_grade_formset'] = SeatGradeFormSet(instance=self.object)
            context['booking_site_formset'] = BookingSiteFormSet(instance=self.object)
            context['discount_type_formset'] = DiscountTypeFormSet(instance=self.object)
        else:
            context['genre_filter'] = ''
            # 새 객체 생성 시 빈 폼셋
            context['seat_grade_formset'] = SeatGradeFormSet()
            context['booking_site_formset'] = BookingSiteFormSet()
            context['discount_type_formset'] = DiscountTypeFormSet()
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            performance = form.save()
            
            # 인라인 폼셋 처리
            seat_grade_formset = SeatGradeFormSet(self.request.POST, instance=performance)
            booking_site_formset = BookingSiteFormSet(self.request.POST, instance=performance)
            discount_type_formset = DiscountTypeFormSet(self.request.POST, instance=performance)
            if (seat_grade_formset.is_valid() and booking_site_formset.is_valid() and 
                discount_type_formset.is_valid()):
                seat_grade_formset.save()
                booking_site_formset.save()
                discount_type_formset.save()
                sync_discount_type_grades(performance, discount_type_formset)
                messages.success(self.request, '공연이 성공적으로 등록되었어요')
                return super().form_valid(form)
            else:
                # 폼셋 검증 실패 시 에러 표시
                messages.error(self.request, '입력한 정보를 확인해주세요')
                transaction.set_rollback(True)
                return self.form_invalid(form)
    
    def form_invalid(self, form):
        # 폼셋 검증 실패 시 폼셋을 다시 컨텍스트에 포함
        context = self.get_context_data(form=form)
        if hasattr(self, 'object') and self.object:
            context['seat_grade_formset'] = SeatGradeFormSet(self.request.POST, instance=self.object)
            context['booking_site_formset'] = BookingSiteFormSet(self.request.POST, instance=self.object)
            context['discount_type_formset'] = DiscountTypeFormSet(self.request.POST, instance=self.object)
        else:
            context['seat_grade_formset'] = SeatGradeFormSet(self.request.POST)
            context['booking_site_formset'] = BookingSiteFormSet(self.request.POST)
            context['discount_type_formset'] = DiscountTypeFormSet(self.request.POST)
        return self.render_to_response(context)


class PerformanceUpdateView(LoginRequiredMixin, UpdateView):
    """공연 수정 뷰"""
    model = Performance
    form_class = PerformanceForm
    template_name = 'performance/form.html'
    success_url = reverse_lazy('performance:list')
    
    def get(self, request, *args, **kwargs):
        # GET 요청 시 이전 메시지 제거
        storage = messages.get_messages(request)
        # 모든 메시지를 소비하여 제거
        list(storage)
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre_choices'] = Performance.GENRE_CHOICES
        
        if self.object:
            context['genre_filter'] = self.object.genre
            # 인라인 폼셋 초기화 (기존 데이터 로드)
            context['seat_grade_formset'] = SeatGradeFormSet(instance=self.object)
            context['booking_site_formset'] = BookingSiteFormSet(instance=self.object)
            context['discount_type_formset'] = DiscountTypeFormSet(instance=self.object)
        else:
            context['genre_filter'] = ''
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            performance = form.save()
            
            # 인라인 폼셋 처리
            seat_grade_formset = SeatGradeFormSet(self.request.POST, instance=performance)
            booking_site_formset = BookingSiteFormSet(self.request.POST, instance=performance)
            discount_type_formset = DiscountTypeFormSet(self.request.POST, instance=performance)
            if (seat_grade_formset.is_valid() and booking_site_formset.is_valid() and 
                discount_type_formset.is_valid()):
                seat_grade_formset.save()
                booking_site_formset.save()
                discount_type_formset.save()
                sync_discount_type_grades(performance, discount_type_formset)
                messages.success(self.request, '공연 정보가 성공적으로 수정되었어요')
                return super().form_valid(form)
            else:
                # 폼셋 검증 실패 시 에러 표시
                messages.error(self.request, '입력한 정보를 확인해주세요')
                transaction.set_rollback(True)
                return self.form_invalid(form)

    
    def form_invalid(self, form):
        # 폼셋 검증 실패 시 폼셋을 다시 컨텍스트에 포함
        context = self.get_context_data(form=form)
        context['seat_grade_formset'] = SeatGradeFormSet(self.request.POST, instance=self.object)
        context['booking_site_formset'] = BookingSiteFormSet(self.request.POST, instance=self.object)
        context['discount_type_formset'] = DiscountTypeFormSet(self.request.POST, instance=self.object)
        return self.render_to_response(context)


class PerformanceDeleteView(LoginRequiredMixin, DeleteView):
    """공연 삭제 뷰"""
    model = Performance
    template_name = 'performance/confirm_delete.html'
    success_url = reverse_lazy('performance:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '공연이 성공적으로 삭제되었어요')
        return super().delete(request, *args, **kwargs)
