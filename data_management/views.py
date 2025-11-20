from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json
from .models import ConcertDailySales, ConcertFinalSales
from .forms import ConcertDailySalesForm, ConcertFinalSalesForm, ConcertSalesDailyFormSet
from .constants import AGE_GROUPS, REGIONS, SEOUL_REGIONS, GYEONGGI_REGIONS
from performance.models import Performance


class PerformanceListView(ListView):
    """매출 관리를 위한 공연 목록 뷰 (모든 장르)"""
    model = Performance
    template_name = 'data_management/performance_list.html'
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


class ConcertSalesListView(ListView):
    """콘서트 데일리 매출 상세 뷰 (특정 공연의 매출)"""
    model = ConcertDailySales
    template_name = 'data_management/concert_sales/detail.html'
    context_object_name = 'sales_list'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ConcertDailySales.objects.select_related('performance').all()
        
        # 공연 필터 (필수)
        performance_id = self.request.GET.get('performance') or self.kwargs.get('performance_id')
        if performance_id:
            queryset = queryset.filter(performance_id=performance_id)
        else:
            # 공연이 지정되지 않으면 빈 쿼리셋 반환
            queryset = queryset.none()
        
        # 날짜 범위 필터
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        if date_start:
            queryset = queryset.filter(date__gte=date_start)
        if date_end:
            queryset = queryset.filter(date__lte=date_end)
        
        # 예매처 필터
        booking_site = self.request.GET.get('booking_site')
        if booking_site:
            queryset = queryset.filter(booking_site__icontains=booking_site)
        
        return queryset.order_by('-date', 'booking_site')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        performance_id = self.request.GET.get('performance') or self.kwargs.get('performance_id')
        
        if performance_id:
            try:
                performance = Performance.objects.get(id=performance_id)
                context['performance'] = performance
                
                # 예매처 목록 추출
                booking_sites = []
                if performance.booking_sites:
                    for site_dict in performance.booking_sites:
                        if isinstance(site_dict, dict):
                            booking_sites.extend(site_dict.keys())
                context['booking_sites'] = json.dumps(booking_sites, ensure_ascii=False)
                
                # 좌석 등급 추출 (템플릿용 리스트 + JavaScript용 JSON)
                seat_grades = performance.seat_grades if performance.seat_grades else []
                context['seat_grades'] = seat_grades
                context['seat_grades_json'] = json.dumps(seat_grades, ensure_ascii=False)
                
                # 할인권종 추출 (템플릿용 리스트 + JavaScript용 JSON)
                discount_types = performance.discount_types if performance.discount_types else []
                context['discount_types'] = discount_types
                context['discount_types_json'] = json.dumps(discount_types, ensure_ascii=False)
                
                # 판매 기간 날짜 리스트 생성
                date_list = []
                if performance.sales_start and performance.sales_end:
                    current_date = performance.sales_start
                    while current_date <= performance.sales_end:
                        date_list.append(current_date.strftime('%Y-%m-%d'))
                        current_date += timedelta(days=1)
                context['sales_date_list'] = json.dumps(date_list, ensure_ascii=False)
                
                # 재사용 가능한 상수들 추가 (템플릿용 리스트 + JavaScript용 JSON)
                context['age_groups'] = AGE_GROUPS
                context['age_groups_json'] = json.dumps(AGE_GROUPS, ensure_ascii=False)
                context['regions'] = REGIONS
                context['regions_json'] = json.dumps(REGIONS, ensure_ascii=False)
                context['seoul_regions'] = SEOUL_REGIONS
                context['seoul_regions_json'] = json.dumps(SEOUL_REGIONS, ensure_ascii=False)
                context['gyeonggi_regions'] = GYEONGGI_REGIONS
                context['gyeonggi_regions_json'] = json.dumps(GYEONGGI_REGIONS, ensure_ascii=False)
                
            except Performance.DoesNotExist:
                context['performance'] = None
                context['booking_sites'] = '[]'
                context['seat_grades'] = []
                context['seat_grades_json'] = '[]'
                context['discount_types'] = []
                context['discount_types_json'] = '[]'
                context['sales_date_list'] = '[]'
                context['age_groups'] = AGE_GROUPS
                context['age_groups_json'] = json.dumps(AGE_GROUPS, ensure_ascii=False)
                context['regions'] = REGIONS
                context['regions_json'] = json.dumps(REGIONS, ensure_ascii=False)
                context['seoul_regions'] = SEOUL_REGIONS
                context['seoul_regions_json'] = json.dumps(SEOUL_REGIONS, ensure_ascii=False)
                context['gyeonggi_regions'] = GYEONGGI_REGIONS
                context['gyeonggi_regions_json'] = json.dumps(GYEONGGI_REGIONS, ensure_ascii=False)
        else:
            context['performance'] = None
            context['booking_sites'] = '[]'
            context['seat_grades'] = []
            context['seat_grades_json'] = '[]'
            context['discount_types'] = []
            context['discount_types_json'] = '[]'
            context['sales_date_list'] = '[]'
            context['age_groups'] = AGE_GROUPS
            context['age_groups_json'] = json.dumps(AGE_GROUPS, ensure_ascii=False)
            context['regions'] = REGIONS
            context['regions_json'] = json.dumps(REGIONS, ensure_ascii=False)
            context['seoul_regions'] = SEOUL_REGIONS
            context['seoul_regions_json'] = json.dumps(SEOUL_REGIONS, ensure_ascii=False)
            context['gyeonggi_regions'] = GYEONGGI_REGIONS
            context['gyeonggi_regions_json'] = json.dumps(GYEONGGI_REGIONS, ensure_ascii=False)
        
        context['performance_filter'] = performance_id or ''
        context['date_start'] = self.request.GET.get('date_start', '')
        context['date_end'] = self.request.GET.get('date_end', '')
        context['booking_site_filter'] = self.request.GET.get('booking_site', '')
        return context


class ConcertSalesCreateView(CreateView):
    """콘서트 데일리 매출 생성 뷰"""
    model = ConcertDailySales
    form_class = ConcertDailySalesForm
    template_name = 'data_management/concert_sales/form.html'
    
    def get_success_url(self):
        performance_id = self.object.performance.id
        return reverse_lazy('data_management:concert_sales_detail', kwargs={'performance_id': performance_id})
    
    def get_initial(self):
        initial = super().get_initial()
        # URL에서 공연 ID 가져오기 (콘서트만)
        performance_id = self.kwargs.get('performance_id') or self.request.GET.get('performance')
        if performance_id:
            try:
                performance = Performance.objects.get(id=performance_id, genre='concert')
                initial['performance'] = performance.id
            except Performance.DoesNotExist:
                pass
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 콘서트 공연 목록만
        context['concerts'] = Performance.objects.filter(genre='concert').order_by('-created_at')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '매출이 성공적으로 등록되었어요')
        return super().form_valid(form)


class ConcertSalesUpdateView(UpdateView):
    """콘서트 데일리 매출 수정 뷰"""
    model = ConcertDailySales
    form_class = ConcertDailySalesForm
    template_name = 'data_management/concert_sales/form.html'
    
    def get_success_url(self):
        performance_id = self.object.performance.id
        return reverse_lazy('data_management:concert_sales_detail', kwargs={'performance_id': performance_id})
    
    def get(self, request, *args, **kwargs):
        # GET 요청 시 이전 메시지 제거
        storage = messages.get_messages(request)
        list(storage)
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 콘서트 공연 목록만
        context['concerts'] = Performance.objects.filter(genre='concert').order_by('-created_at')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '매출 정보가 성공적으로 수정되었어요')
        return super().form_valid(form)


class ConcertSalesDeleteView(DeleteView):
    """콘서트 데일리 매출 삭제 뷰"""
    model = ConcertDailySales
    template_name = 'data_management/concert_sales/confirm_delete.html'
    
    def get_success_url(self):
        performance_id = self.object.performance.id
        return reverse_lazy('data_management:concert_sales_detail', kwargs={'performance_id': performance_id})
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '매출이 성공적으로 삭제되었어요')
        return super().delete(request, *args, **kwargs)


class MusicalSalesListView(ListView):
    """뮤지컬 매출 목록 뷰 (준비 중)"""
    template_name = 'data_management/sales_coming_soon.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        performance_id = self.kwargs.get('performance_id')
        if performance_id:
            try:
                context['performance'] = Performance.objects.get(id=performance_id, genre='musical')
                context['genre'] = '뮤지컬'
            except Performance.DoesNotExist:
                context['performance'] = None
        return context


class TheaterSalesListView(ListView):
    """연극 매출 목록 뷰 (준비 중)"""
    template_name = 'data_management/sales_coming_soon.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        performance_id = self.kwargs.get('performance_id')
        if performance_id:
            try:
                context['performance'] = Performance.objects.get(id=performance_id, genre='theater')
                context['genre'] = '연극'
            except Performance.DoesNotExist:
                context['performance'] = None
        return context


@login_required
@require_http_methods(["POST"])
def save_daily_sales(request, performance_id):
    """날짜별 데일리 매출 저장 (AJAX)"""
    try:
        performance = Performance.objects.get(id=performance_id, genre='concert')
    except Performance.DoesNotExist:
        return JsonResponse({'success': False, 'error': '공연을 찾을 수 없어요'}, status=404)
    
    # POST 데이터에서 날짜 추출
    date_str = request.POST.get('date')
    if not date_str:
        return JsonResponse({'success': False, 'error': '날짜가 필요해요'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'success': False, 'error': '올바른 날짜 형식이 아니에요'}, status=400)
    
    # 예매처 목록 추출
    booking_sites = []
    if performance.booking_sites:
        for site_dict in performance.booking_sites:
            if isinstance(site_dict, dict):
                booking_sites.extend(site_dict.keys())
    
    if not booking_sites:
        return JsonResponse({'success': False, 'error': '등록된 예매처가 없어요'}, status=400)
    
    # 좌석 등급 추출
    seat_grades = performance.seat_grades if performance.seat_grades else []
    
    # 기존 데이터 삭제 (해당 날짜의 데일리 매출만)
    ConcertDailySales.objects.filter(
        performance=performance,
        date=date
    ).delete()
    
    # Formset 데이터 준비
    formset_data = {}
    formset_files = {}
    
    # 각 예매처별로 폼 데이터 준비
    for idx, booking_site in enumerate(booking_sites):
        prefix = f'form-{idx}'
        formset_data[f'{prefix}-performance'] = performance.id
        formset_data[f'{prefix}-date'] = date_str
        formset_data[f'{prefix}-booking_site'] = booking_site
        formset_data[f'{prefix}-paid_revenue'] = request.POST.get(f'{booking_site}_paid_revenue', '0') or '0'
        formset_data[f'{prefix}-paid_ticket_count'] = request.POST.get(f'{booking_site}_paid_ticket_count', '0') or '0'
        formset_data[f'{prefix}-unpaid_revenue'] = request.POST.get(f'{booking_site}_unpaid_revenue', '0') or '0'
        formset_data[f'{prefix}-unpaid_ticket_count'] = request.POST.get(f'{booking_site}_unpaid_ticket_count', '0') or '0'
        
        # 등급별 매수
        paid_by_grade = {}
        unpaid_by_grade = {}
        free_by_grade = {}
        
        for grade in seat_grades:
            paid_value = request.POST.get(f'{booking_site}_paid_grade_{grade}', '0') or '0'
            unpaid_value = request.POST.get(f'{booking_site}_unpaid_grade_{grade}', '0') or '0'
            free_value = request.POST.get(f'{booking_site}_free_grade_{grade}', '0') or '0'
            
            if int(paid_value) > 0:
                paid_by_grade[grade] = int(paid_value)
            if int(unpaid_value) > 0:
                unpaid_by_grade[grade] = int(unpaid_value)
            if int(free_value) > 0:
                free_by_grade[grade] = int(free_value)
        
        formset_data[f'{prefix}-paid_by_grade'] = json.dumps(paid_by_grade, ensure_ascii=False)
        formset_data[f'{prefix}-unpaid_by_grade'] = json.dumps(unpaid_by_grade, ensure_ascii=False)
        formset_data[f'{prefix}-free_by_grade'] = json.dumps(free_by_grade, ensure_ascii=False)
    
    formset_data['form-TOTAL_FORMS'] = len(booking_sites)
    formset_data['form-INITIAL_FORMS'] = '0'
    formset_data['form-MIN_NUM_FORMS'] = '0'
    formset_data['form-MAX_NUM_FORMS'] = '1000'
    
    # Formset 생성 및 검증
    formset = ConcertSalesDailyFormSet(formset_data, formset_files, queryset=ConcertDailySales.objects.none())
    
    # 각 폼에 좌석 등급 전달
    for form in formset.forms:
        form.seat_grades = seat_grades
    
    if formset.is_valid():
        formset.save()
        return JsonResponse({'success': True, 'message': '매출이 성공적으로 저장되었어요'})
    else:
        errors = {}
        for idx, form in enumerate(formset.forms):
            if form.errors:
                errors[f'form_{idx}'] = form.errors
        return JsonResponse({'success': False, 'error': '입력값을 확인해주세요', 'errors': errors}, status=400)
