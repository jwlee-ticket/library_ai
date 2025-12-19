from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from core.mixins import CompanyFilterMixin
from .models import Performance, Person
from .forms import PerformanceForm, SeatGradeFormSet, BookingSiteFormSet, DiscountTypeFormSet, CastingRoleFormSet


class PerformanceListView(CompanyFilterMixin, ListView):
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


class PerformanceDetailView(CompanyFilterMixin, DetailView):
    """공연 상세 뷰"""
    model = Performance
    template_name = 'performance/detail.html'
    context_object_name = 'performance'


class PerformanceCreateView(CompanyFilterMixin, CreateView):
    """공연 생성 뷰"""
    model = Performance
    form_class = PerformanceForm
    template_name = 'performance/form.html'
    success_url = reverse_lazy('performance:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre_choices'] = Performance.GENRE_CHOICES
        
        # Person 쿼리셋 필터링
        if self.request.user.is_superuser:
            person_queryset = Person.objects.all()
        else:
            user_profile = getattr(self.request.user, 'profile', None)
            if user_profile and user_profile.company:
                person_queryset = Person.objects.filter(company=user_profile.company)
            else:
                person_queryset = Person.objects.none()
        
        context['person_choices'] = person_queryset.order_by('name')
        if self.object:
            context['genre_filter'] = self.object.genre
            # 인라인 폼셋 초기화
            context['seat_grade_formset'] = SeatGradeFormSet(instance=self.object)
            context['booking_site_formset'] = BookingSiteFormSet(instance=self.object)
            context['discount_type_formset'] = DiscountTypeFormSet(instance=self.object)
            context['casting_role_formset'] = CastingRoleFormSet(instance=self.object)
        else:
            context['genre_filter'] = ''
            # 새 객체 생성 시 빈 폼셋
            context['seat_grade_formset'] = SeatGradeFormSet()
            context['booking_site_formset'] = BookingSiteFormSet()
            context['discount_type_formset'] = DiscountTypeFormSet()
            context['casting_role_formset'] = CastingRoleFormSet()
        return context
    
    def form_valid(self, form):
        performance = form.save()
        
        # 인라인 폼셋 처리
        seat_grade_formset = SeatGradeFormSet(self.request.POST, instance=performance)
        booking_site_formset = BookingSiteFormSet(self.request.POST, instance=performance)
        discount_type_formset = DiscountTypeFormSet(self.request.POST, instance=performance)
        casting_role_formset = CastingRoleFormSet(self.request.POST, instance=performance)
        
        if (seat_grade_formset.is_valid() and booking_site_formset.is_valid() and 
            discount_type_formset.is_valid() and casting_role_formset.is_valid()):
            seat_grade_formset.save()
            booking_site_formset.save()
            discount_type_formset.save()
            casting_role_formset.save()
            messages.success(self.request, '공연이 성공적으로 등록되었어요')
            return super().form_valid(form)
        else:
            # 폼셋 검증 실패 시 에러 표시
            messages.error(self.request, '입력한 정보를 확인해주세요')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        # 폼셋 검증 실패 시 폼셋을 다시 컨텍스트에 포함
        context = self.get_context_data(form=form)
        if hasattr(self, 'object') and self.object:
            context['seat_grade_formset'] = SeatGradeFormSet(self.request.POST, instance=self.object)
            context['booking_site_formset'] = BookingSiteFormSet(self.request.POST, instance=self.object)
            context['discount_type_formset'] = DiscountTypeFormSet(self.request.POST, instance=self.object)
            context['casting_role_formset'] = CastingRoleFormSet(self.request.POST, instance=self.object)
        else:
            context['seat_grade_formset'] = SeatGradeFormSet(self.request.POST)
            context['booking_site_formset'] = BookingSiteFormSet(self.request.POST)
            context['discount_type_formset'] = DiscountTypeFormSet(self.request.POST)
            context['casting_role_formset'] = CastingRoleFormSet(self.request.POST)
        return self.render_to_response(context)


class PerformanceUpdateView(CompanyFilterMixin, UpdateView):
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
        
        # Person 쿼리셋 필터링
        if self.request.user.is_superuser:
            person_queryset = Person.objects.all()
        else:
            user_profile = getattr(self.request.user, 'profile', None)
            if user_profile and user_profile.company:
                person_queryset = Person.objects.filter(company=user_profile.company)
            else:
                person_queryset = Person.objects.none()
        
        context['person_choices'] = person_queryset.order_by('name')
        if self.object:
            context['genre_filter'] = self.object.genre
            # 인라인 폼셋 초기화 (기존 데이터 로드)
            context['seat_grade_formset'] = SeatGradeFormSet(instance=self.object)
            context['booking_site_formset'] = BookingSiteFormSet(instance=self.object)
            context['discount_type_formset'] = DiscountTypeFormSet(instance=self.object)
            context['casting_role_formset'] = CastingRoleFormSet(instance=self.object)
        else:
            context['genre_filter'] = ''
        return context
    
    def form_valid(self, form):
        performance = form.save()
        
        # 인라인 폼셋 처리
        seat_grade_formset = SeatGradeFormSet(self.request.POST, instance=performance)
        booking_site_formset = BookingSiteFormSet(self.request.POST, instance=performance)
        discount_type_formset = DiscountTypeFormSet(self.request.POST, instance=performance)
        casting_role_formset = CastingRoleFormSet(self.request.POST, instance=performance)
        
        if (seat_grade_formset.is_valid() and booking_site_formset.is_valid() and 
            discount_type_formset.is_valid() and casting_role_formset.is_valid()):
            seat_grade_formset.save()
            booking_site_formset.save()
            discount_type_formset.save()
            casting_role_formset.save()
            messages.success(self.request, '공연 정보가 성공적으로 수정되었어요')
            return super().form_valid(form)
        else:
            # 폼셋 검증 실패 시 에러 표시
            messages.error(self.request, '입력한 정보를 확인해주세요')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        # 폼셋 검증 실패 시 폼셋을 다시 컨텍스트에 포함
        context = self.get_context_data(form=form)
        context['seat_grade_formset'] = SeatGradeFormSet(self.request.POST, instance=self.object)
        context['booking_site_formset'] = BookingSiteFormSet(self.request.POST, instance=self.object)
        context['discount_type_formset'] = DiscountTypeFormSet(self.request.POST, instance=self.object)
        context['casting_role_formset'] = CastingRoleFormSet(self.request.POST, instance=self.object)
        return self.render_to_response(context)


class PerformanceDeleteView(CompanyFilterMixin, DeleteView):
    """공연 삭제 뷰"""
    model = Performance
    template_name = 'performance/confirm_delete.html'
    success_url = reverse_lazy('performance:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '공연이 성공적으로 삭제되었어요')
        return super().delete(request, *args, **kwargs)
