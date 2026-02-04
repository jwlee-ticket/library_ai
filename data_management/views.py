from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json
import re
from decimal import Decimal
import pandas as pd
from django.db import transaction
import os
from .models import PerformanceDailySales, PerformanceFinalSales, PerformanceDailySalesGrade, PerformanceSalesUploadLog
from .forms import PerformanceDailySalesForm, PerformanceFinalSalesForm, PerformanceSalesDailyFormSet, PerformanceSalesExcelUploadForm
from .constants import AGE_GROUPS, REGIONS, SEOUL_REGIONS, GYEONGGI_REGIONS
from performance.models import Performance, BookingSite, SeatGrade


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


class PerformanceSalesDetailView(ListView):
    """공연 데일리 매출 상세 뷰 (특정 공연의 매출)"""
    model = PerformanceDailySales
    template_name = 'data_management/concert_sales/detail.html'
    context_object_name = 'sales_list'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PerformanceDailySales.objects.select_related('performance').all()
        
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
            queryset = queryset.filter(booking_site__name__icontains=booking_site)
        
        return queryset.order_by('-date', 'booking_site')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        performance_id = self.request.GET.get('performance') or self.kwargs.get('performance_id')
        
        if performance_id:
            try:
                performance = Performance.objects.get(id=performance_id)
                context['performance'] = performance
                
                # 예매처 목록 추출
                booking_sites = [site.name for site in performance.booking_sites.all()]
                context['booking_sites'] = json.dumps(booking_sites, ensure_ascii=False)
                
                # 좌석 등급 추출 (템플릿용 리스트 + JavaScript용 JSON)
                seat_grades = [grade.name for grade in performance.seat_grades.all()]
                context['seat_grades'] = seat_grades
                context['seat_grades_json'] = json.dumps(seat_grades, ensure_ascii=False)
                
                # 할인권종 추출 (템플릿용 리스트 + JavaScript용 JSON)
                discount_types = [{'name': dt.name, 'start_date': dt.start_date.strftime('%Y-%m-%d'), 'end_date': dt.end_date.strftime('%Y-%m-%d'), 'discount_rate': dt.discount_rate} for dt in performance.discount_types.all()]
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
                
                # 실제 저장된 매출 데이터가 있는 날짜 리스트
                saved_dates = PerformanceDailySales.objects.filter(
                    performance=performance
                ).values_list('date', flat=True).distinct()
                saved_date_list = [date.strftime('%Y-%m-%d') for date in saved_dates]
                context['saved_date_list'] = json.dumps(saved_date_list, ensure_ascii=False)
                
                # 재사용 가능한 상수들 추가 (템플릿용 리스트 + JavaScript용 JSON)
                context['age_groups'] = AGE_GROUPS
                context['age_groups_json'] = json.dumps(AGE_GROUPS, ensure_ascii=False)
                context['regions'] = REGIONS
                context['regions_json'] = json.dumps(REGIONS, ensure_ascii=False)
                context['seoul_regions'] = SEOUL_REGIONS
                context['seoul_regions_json'] = json.dumps(SEOUL_REGIONS, ensure_ascii=False)
                context['gyeonggi_regions'] = GYEONGGI_REGIONS
                context['gyeonggi_regions_json'] = json.dumps(GYEONGGI_REGIONS, ensure_ascii=False)
                
                context['upload_logs'] = PerformanceSalesUploadLog.objects.filter(
                    performance=performance
                ).order_by('-uploaded_at')
                
            except Performance.DoesNotExist:
                context['performance'] = None
                context['booking_sites'] = '[]'
                context['seat_grades'] = []
                context['seat_grades_json'] = '[]'
                context['discount_types'] = []
                context['discount_types_json'] = '[]'
                context['sales_date_list'] = '[]'
                context['saved_date_list'] = '[]'
                context['upload_logs'] = []
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
            context['saved_date_list'] = '[]'
            context['upload_logs'] = []
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


class PerformanceSalesCreateView(CreateView):
    """공연 데일리 매출 생성 뷰"""
    model = PerformanceDailySales
    form_class = PerformanceDailySalesForm
    template_name = 'data_management/concert_sales/form.html'
    
    def get_success_url(self):
        performance_id = self.object.performance.id
        return reverse_lazy('data_management:performance_sales_detail', kwargs={'performance_id': performance_id})
    
    def get_initial(self):
        initial = super().get_initial()
        # URL에서 공연 ID 가져오기
        performance_id = self.kwargs.get('performance_id') or self.request.GET.get('performance')
        if performance_id:
            try:
                performance = Performance.objects.get(id=performance_id)
                initial['performance'] = performance.id
            except Performance.DoesNotExist:
                pass
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['performances'] = Performance.objects.all().order_by('-created_at')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '매출이 성공적으로 등록되었어요')
        return super().form_valid(form)


class PerformanceSalesUpdateView(UpdateView):
    """공연 데일리 매출 수정 뷰"""
    model = PerformanceDailySales
    form_class = PerformanceDailySalesForm
    template_name = 'data_management/concert_sales/form.html'
    
    def get_success_url(self):
        performance_id = self.object.performance.id
        return reverse_lazy('data_management:performance_sales_detail', kwargs={'performance_id': performance_id})
    
    def get(self, request, *args, **kwargs):
        # GET 요청 시 이전 메시지 제거
        storage = messages.get_messages(request)
        list(storage)
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['performances'] = Performance.objects.all().order_by('-created_at')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '매출 정보가 성공적으로 수정되었어요')
        return super().form_valid(form)


class PerformanceSalesDeleteView(DeleteView):
    """공연 데일리 매출 삭제 뷰"""
    model = PerformanceDailySales
    template_name = 'data_management/concert_sales/confirm_delete.html'
    
    def get_success_url(self):
        performance_id = self.object.performance.id
        return reverse_lazy('data_management:performance_sales_detail', kwargs={'performance_id': performance_id})
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '매출이 성공적으로 삭제되었어요')
        return super().delete(request, *args, **kwargs)


def _normalize_text(value):
    if value is None:
        return ''
    text = str(value).strip()
    if text.lower() == 'nan':
        return ''
    return text


def _is_valid_seat_grade_label(label):
    if not label:
        return False
    normalized = _normalize_text(label)
    if not normalized:
        return False
    if normalized in ['TOT', '금액']:
        return True
    if re.fullmatch(r'[0-9,.\s]+', normalized):
        return False
    ignore_keywords = [
        '수량', '매수', '합계', '총계', '전체', '계', 'TOTAL', 'TOTALS', 'SUM',
        '입금', '미입금', '무료', '유료', '비고', '단가'
    ]
    if any(keyword in normalized for keyword in ignore_keywords):
        return False
    return True


def _safe_int(value):
    if value is None:
        return 0
    if isinstance(value, (int, float)) and not pd.isna(value):
        return int(value)
    text = _normalize_text(value)
    if not text:
        return 0
    text = text.replace(',', '')
    try:
        return int(float(text))
    except ValueError:
        return 0


def _parse_date(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return pd.to_datetime(value).date()
    except ValueError:
        return None


def _find_header_row(df):
    for idx in range(len(df)):
        row = df.iloc[idx].astype(str).tolist()
        row_text = ' '.join(row)
        if ('No.' in row_text or 'No' in row_text or '회차' in row_text) and ('Date' in row_text or '공연일' in row_text):
            return idx
    return None


def _classify_group(label):
    text = _normalize_text(label)
    if not text:
        return None
    
    ignore_keywords = [
        '유료 계', '전체', '점유율', '잔여', '객단가', '할인율',
        'BEP', '목표매출', '추가 필요', '미입금 내역', '합계', '총계'
    ]
    if any(keyword in text for keyword in ignore_keywords):
        return None
    
    if text in ['미', '미지정', '합계', 'TOTAL', '계', '전체', '총계']:
        return None
    
    if '미입금' in text and '입금+미입금' not in text and '미입금포함' not in text:
        return None
    
    status = None
    if '입금+미입금' in text or '미입금포함' in text:
        status = 'total'
    elif '입금' in text:
        status = 'paid'
    elif '초대' in text or '무료' in text:
        status = 'free'
    
    if not status:
        return None
    
    if status == 'free':
        return (None, status)
    
    booking_site = re.sub(r'\(.*?\)', '', text)
    booking_site = booking_site.replace('입금+미입금', '').replace('입금', '').replace('미입금포함', '')
    booking_site = booking_site.strip()
    return (booking_site or None, status)


def _is_summary_row(no_value):
    text = _normalize_text(no_value)
    if not text:
        return True
    summary_keywords = ['TOTAL', '계', '합계', '공연 계']
    return any(keyword in text for keyword in summary_keywords)


def _parse_sales_excel(excel_file, performance):
    excel_file.seek(0)
    xls = pd.ExcelFile(excel_file)
    sheet_candidates = ['회차별판매', '회차별 판매', 'Seat details']
    sheet_name = next((name for name in sheet_candidates if name in xls.sheet_names), None)
    if not sheet_name:
        raise ValueError('회차별판매 시트를 찾을 수 없어요')
    
    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
    if df.empty:
        raise ValueError('회차별판매 시트가 비어 있어요')
    
    header_row_idx = _find_header_row(df)
    if header_row_idx is None:
        raise ValueError('헤더 행을 찾을 수 없어요 (No./Date/Time)')
    
    header_row = df.iloc[header_row_idx].tolist()
    group_row = df.iloc[header_row_idx - 1] if header_row_idx > 0 else pd.Series([None] * len(header_row))
    group_row = group_row.ffill()
    
    header_texts = [_normalize_text(value) for value in header_row]
    group_texts = [_normalize_text(value) for value in group_row.tolist()]
    
    def _find_col_index(candidates):
        for idx, name in enumerate(header_texts):
            if name in candidates:
                return idx
        return None
    
    no_idx = _find_col_index(['No.', 'No', '회차'])
    date_idx = _find_col_index(['Date', '공연일'])
    time_idx = _find_col_index(['Time', '시간'])
    
    if date_idx is None:
        raise ValueError('공연일(Date) 컬럼을 찾을 수 없어요')
    
    first_group_idx = None
    for idx, label in enumerate(group_texts):
        if _classify_group(label):
            first_group_idx = idx
            break
    
    cast_cols = []
    if time_idx is not None and first_group_idx is not None and first_group_idx > time_idx:
        cast_cols = list(range(time_idx + 1, first_group_idx))
    
    column_map = []
    seat_grade_names = set()
    for idx, (group_label, header_label) in enumerate(zip(group_texts, header_texts)):
        group_info = _classify_group(group_label)
        if not group_info:
            continue
        booking_site_name, status = group_info
        grade_label = _normalize_text(header_label)
        if not grade_label:
            continue
        
        if grade_label in ['TOT', '금액']:
            column_map.append({
                'index': idx,
                'booking_site': booking_site_name,
                'status': status,
                'grade': grade_label
            })
            continue

        if not _is_valid_seat_grade_label(grade_label):
            continue
        
        seat_grade_names.add(grade_label)
        column_map.append({
            'index': idx,
            'booking_site': booking_site_name,
            'status': status,
            'grade': grade_label
        })
    
    aggregates = {}
    rounds_by_date = {}
    dates_in_file = set()
    
    date_series = df.iloc[header_row_idx + 1:, date_idx].ffill()

    file_date_override = None
    filename = os.path.basename(getattr(excel_file, 'name', ''))
    match = re.search(r'(\d{4})(?=\\.[^.]+$)', filename)
    if match:
        month = int(match.group(1)[:2])
        day = int(match.group(1)[2:])
        base_year = performance.performance_start.year if performance.performance_start else datetime.now().year
        if performance.performance_start and month < performance.performance_start.month:
            base_year += 1
        try:
            file_date_override = datetime(base_year, month, day).date()
        except ValueError:
            file_date_override = None

    unique_dates = set()
    for value in date_series:
        parsed = _parse_date(value)
        if parsed:
            unique_dates.add(parsed)
    force_date_override = bool(file_date_override and (not unique_dates or (len(unique_dates) == 1 and file_date_override not in unique_dates)))

    for row_idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[row_idx]
        no_value = row[no_idx] if no_idx is not None else None
        if _is_summary_row(no_value):
            continue
        
        date_value = date_series.iloc[row_idx - (header_row_idx + 1)]
        parsed_date = _parse_date(date_value)
        if force_date_override and file_date_override:
            parsed_date = file_date_override
        if not parsed_date:
            continue
        
        dates_in_file.add(parsed_date)
        
        cast_info = {}
        for cast_col in cast_cols:
            role = _normalize_text(header_texts[cast_col])
            person = _normalize_text(row[cast_col])
            if role and person:
                cast_info[role] = person
        
        if parsed_date not in rounds_by_date:
            rounds_by_date[parsed_date] = []
        
        time_value = _normalize_text(row[time_idx]) if time_idx is not None else ''
        rounds_by_date[parsed_date].append({
            'no': _normalize_text(no_value),
            'time': time_value,
            'cast': cast_info
        })
        
        for col in column_map:
            value = _safe_int(row[col['index']])
            booking_site_name = col['booking_site']
            status = col['status']
            grade_label = col['grade']
            
            key = (parsed_date, booking_site_name)
            if key not in aggregates:
                aggregates[key] = {
                    'paid_revenue': 0,
                    'paid_ticket_count': 0,
                    'total_revenue': 0,
                    'total_ticket_count': 0,
                    'grades_paid': {},
                    'grades_total': {},
                    'grades_free': {}
                }
            
            if status in ['paid', 'total']:
                if grade_label == 'TOT':
                    if status == 'paid':
                        aggregates[key]['paid_ticket_count'] += value
                    else:
                        aggregates[key]['total_ticket_count'] += value
                elif grade_label == '금액':
                    if status == 'paid':
                        aggregates[key]['paid_revenue'] += value
                    else:
                        aggregates[key]['total_revenue'] += value
                else:
                    target = 'grades_paid' if status == 'paid' else 'grades_total'
                    aggregates[key][target][grade_label] = aggregates[key][target].get(grade_label, 0) + value
            elif status == 'free':
                if grade_label not in ['TOT', '금액']:
                    aggregates[key]['grades_free'][grade_label] = aggregates[key]['grades_free'].get(grade_label, 0) + value
    
    return {
        'aggregates': aggregates,
        'rounds_by_date': rounds_by_date,
        'seat_grade_names': seat_grade_names,
        'dates_in_file': dates_in_file,
        'sheet_name': sheet_name,
    }


@login_required
@require_http_methods(["POST"])
def upload_sales_excel(request, performance_id):
    """공연 매출 엑셀 업로드 처리"""
    performance = get_object_or_404(Performance, id=performance_id)
    form = PerformanceSalesExcelUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'success': False, 'error': '입력값을 확인해주세요', 'errors': form.errors}, status=400)
    
    excel_file = form.cleaned_data['excel_file']
    
    try:
        parsed = _parse_sales_excel(excel_file, performance)
    except ValueError as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=400)
    
    aggregates = parsed['aggregates']
    if not aggregates:
        return JsonResponse({'success': False, 'error': '저장할 매출 데이터가 없어요'}, status=400)
    
    seat_grade_names = parsed['seat_grade_names']
    dates_in_file = parsed['dates_in_file']
    rounds_by_date = parsed['rounds_by_date']
    sheet_name = parsed.get('sheet_name', '')

    date_start = min(dates_in_file) if dates_in_file else None
    date_end = max(dates_in_file) if dates_in_file else None
    
    with transaction.atomic():
        upload_log = PerformanceSalesUploadLog.objects.create(
            performance=performance,
            original_filename=excel_file.name,
            sheet_name=sheet_name,
            date_start=date_start,
            date_end=date_end,
            daily_sales_count=0,
            grade_sales_count=0,
            status='success',
        )

        PerformanceDailySales.objects.filter(
            performance=performance,
            date__in=list(dates_in_file)
        ).delete()
        
        daily_sales_count = 0
        grade_sales_count = 0
        
        seat_grade_map = {}
        seat_grade_order = SeatGrade.objects.filter(performance=performance).count()
        for grade_name in seat_grade_names:
            seat_grade, created = SeatGrade.objects.get_or_create(
                performance=performance,
                name=grade_name,
                defaults={
                    'price': 0,
                    'seat_count': 0,
                    'order': seat_grade_order
                }
            )
            if created:
                seat_grade_order += 1
            seat_grade_map[grade_name] = seat_grade
        
        booking_site_map = {}
        for _, booking_site_name in aggregates.keys():
            if not booking_site_name:
                continue
            if booking_site_name in booking_site_map:
                continue
            booking_site, _ = BookingSite.objects.get_or_create(
                performance=performance,
                name=booking_site_name
            )
            booking_site_map[booking_site_name] = booking_site
        
        for (sale_date, booking_site_name), data in aggregates.items():
            booking_site = booking_site_map.get(booking_site_name) if booking_site_name else None
            
            total_revenue = data['total_revenue']
            total_ticket_count = data['total_ticket_count']
            unpaid_revenue = max(total_revenue - data['paid_revenue'], 0) if total_revenue else 0
            unpaid_ticket_count = max(total_ticket_count - data['paid_ticket_count'], 0) if total_ticket_count else 0

            has_grade_data = any(
                value > 0 for value in (
                    list(data['grades_paid'].values()) +
                    list(data['grades_total'].values()) +
                    list(data['grades_free'].values())
                )
            )
            has_base_data = any([
                data['paid_revenue'],
                data['paid_ticket_count'],
                unpaid_revenue,
                unpaid_ticket_count
            ])
            if not has_base_data and not has_grade_data:
                continue
            
            notes = {
                'source': 'excel',
                'rounds': rounds_by_date.get(sale_date, [])
            }
            
            daily_sales = PerformanceDailySales.objects.create(
                performance=performance,
                date=sale_date,
                booking_site=booking_site,
                upload_log=upload_log,
                paid_revenue=Decimal(data['paid_revenue']),
                paid_ticket_count=data['paid_ticket_count'],
                unpaid_revenue=Decimal(unpaid_revenue),
                unpaid_ticket_count=unpaid_ticket_count,
                notes=json.dumps(notes, ensure_ascii=False)
            )
            daily_sales_count += 1
            
            for grade_name in seat_grade_names:
                paid_count = data['grades_paid'].get(grade_name, 0)
                total_count = data['grades_total'].get(grade_name, paid_count)
                unpaid_count = max(total_count - paid_count, 0) if total_count else 0
                free_count = data['grades_free'].get(grade_name, 0)
                
                if paid_count == 0 and unpaid_count == 0 and free_count == 0:
                    continue
                
                PerformanceDailySalesGrade.objects.create(
                    daily_sales=daily_sales,
                    seat_grade=seat_grade_map[grade_name],
                    paid_count=paid_count,
                    unpaid_count=unpaid_count,
                    free_count=free_count
                )
                grade_sales_count += 1
    
        upload_log.daily_sales_count = daily_sales_count
        upload_log.grade_sales_count = grade_sales_count
        upload_log.save(update_fields=['daily_sales_count', 'grade_sales_count'])
    delete_url = reverse('data_management:performance_sales_upload_log_delete', args=[performance.id, upload_log.id])
    
    return JsonResponse({
        'success': True,
        'message': '엑셀 업로드가 완료되었습니다.',
        'daily_sales_count': daily_sales_count,
        'grade_sales_count': grade_sales_count,
        'date_count': len(dates_in_file),
        'file_name': excel_file.name,
        'sheet_name': sheet_name,
        'date_start': date_start.strftime('%Y-%m-%d') if date_start else '',
        'date_end': date_end.strftime('%Y-%m-%d') if date_end else '',
        'upload_log_id': upload_log.id,
        'delete_url': delete_url,
    })


@login_required
@require_http_methods(["POST"])
def delete_sales_upload_log(request, performance_id, log_id):
    """업로드 파일 목록에서 로그 삭제"""
    performance = get_object_or_404(Performance, id=performance_id)
    upload_log = get_object_or_404(PerformanceSalesUploadLog, id=log_id, performance=performance)
    upload_log.delete()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def save_daily_sales(request, performance_id):
    """날짜별 데일리 매출 저장 (AJAX)"""
    try:
        performance = Performance.objects.get(id=performance_id)
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
    booking_sites = list(performance.booking_sites.all())
    booking_site_names = [site.name for site in booking_sites]
    
    if not booking_sites:
        return JsonResponse({'success': False, 'error': '등록된 예매처가 없어요'}, status=400)
    
    # 좌석 등급 추출
    seat_grades = list(performance.seat_grades.all())
    seat_grade_names = [grade.name for grade in seat_grades]
    
    # 기존 데이터 삭제 (해당 날짜의 데일리 매출만)
    PerformanceDailySales.objects.filter(
        performance=performance,
        date=date
    ).delete()
    
    # Formset 데이터 준비
    formset_data = {}
    formset_files = {}
    
    # 각 예매처별로 폼 데이터 준비
    grade_data = {}  # {booking_site_name: {seat_grade_name: {paid, unpaid, free}}}
    
    for idx, booking_site in enumerate(booking_sites):
        prefix = f'form-{idx}'
        booking_site_name = booking_site.name
        formset_data[f'{prefix}-performance'] = performance.id
        formset_data[f'{prefix}-date'] = date_str
        formset_data[f'{prefix}-booking_site'] = booking_site.id
        formset_data[f'{prefix}-paid_revenue'] = request.POST.get(f'{booking_site_name}_paid_revenue', '0') or '0'
        formset_data[f'{prefix}-paid_ticket_count'] = request.POST.get(f'{booking_site_name}_paid_ticket_count', '0') or '0'
        formset_data[f'{prefix}-unpaid_revenue'] = request.POST.get(f'{booking_site_name}_unpaid_revenue', '0') or '0'
        formset_data[f'{prefix}-unpaid_ticket_count'] = request.POST.get(f'{booking_site_name}_unpaid_ticket_count', '0') or '0'
        
        # 등급별 매수 데이터 수집 (나중에 PerformanceDailySalesGrade로 저장)
        grade_data[booking_site_name] = {}
        for seat_grade in seat_grades:
            seat_grade_name = seat_grade.name
            paid_value = request.POST.get(f'{booking_site_name}_paid_grade_{seat_grade_name}', '0') or '0'
            unpaid_value = request.POST.get(f'{booking_site_name}_unpaid_grade_{seat_grade_name}', '0') or '0'
            free_value = request.POST.get(f'{booking_site_name}_free_grade_{seat_grade_name}', '0') or '0'
            
            grade_data[booking_site_name][seat_grade_name] = {
                'seat_grade': seat_grade,
                'paid': int(paid_value),
                'unpaid': int(unpaid_value),
                'free': int(free_value),
            }
    
    formset_data['form-TOTAL_FORMS'] = len(booking_sites)
    formset_data['form-INITIAL_FORMS'] = '0'
    formset_data['form-MIN_NUM_FORMS'] = '0'
    formset_data['form-MAX_NUM_FORMS'] = '1000'
    
    # Formset 생성 및 검증
    formset = PerformanceSalesDailyFormSet(formset_data, formset_files, queryset=PerformanceDailySales.objects.none())
    
    # 각 폼에 좌석 등급 전달
    for form in formset.forms:
        form.seat_grades = seat_grade_names
    
    if formset.is_valid():
        # PerformanceDailySales 저장
        daily_sales_instances = formset.save()
        
        # PerformanceDailySalesGrade 저장
        for daily_sales in daily_sales_instances:
            booking_site_name = daily_sales.booking_site.name if daily_sales.booking_site else None
            if booking_site_name and booking_site_name in grade_data:
                for seat_grade_name, grade_info in grade_data[booking_site_name].items():
                    if grade_info['paid'] > 0 or grade_info['unpaid'] > 0 or grade_info['free'] > 0:
                        PerformanceDailySalesGrade.objects.update_or_create(
                            daily_sales=daily_sales,
                            seat_grade=grade_info['seat_grade'],
                            defaults={
                                'paid_count': grade_info['paid'],
                                'unpaid_count': grade_info['unpaid'],
                                'free_count': grade_info['free'],
                            }
                        )
        
        return JsonResponse({'success': True, 'message': '매출이 성공적으로 저장되었어요'})
    else:
        errors = {}
        for idx, form in enumerate(formset.forms):
            if form.errors:
                errors[f'form_{idx}'] = form.errors
        return JsonResponse({'success': False, 'error': '입력값을 확인해주세요', 'errors': errors}, status=400)


@login_required
@require_http_methods(["GET"])
def get_daily_sales(request, performance_id):
    """특정 날짜의 데일리 매출 조회 (AJAX)"""
    try:
        performance = Performance.objects.get(id=performance_id)
    except Performance.DoesNotExist:
        return JsonResponse({'success': False, 'error': '공연을 찾을 수 없어요'}, status=404)
    
    # GET 파라미터에서 날짜 추출
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'success': False, 'error': '날짜가 필요해요'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'success': False, 'error': '올바른 날짜 형식이 아니에요'}, status=400)
    
    # 해당 날짜의 모든 매출 데이터 조회
    sales_data = PerformanceDailySales.objects.filter(
        performance=performance,
        date=date
    ).select_related('booking_site').prefetch_related('grade_sales__seat_grade')
    
    # 예매처별로 데이터 정리
    result = {}
    for sales in sales_data:
        site = sales.booking_site.name if sales.booking_site else '미지정'
        if site not in result:
            result[site] = {
                'paid_revenue': 0,
                'paid_ticket_count': 0,
                'unpaid_revenue': 0,
                'unpaid_ticket_count': 0,
                'paid_by_grade': {},
                'unpaid_by_grade': {},
                'free_by_grade': {}
            }
        
        result[site]['paid_revenue'] = float(sales.paid_revenue) if sales.paid_revenue else 0
        result[site]['paid_ticket_count'] = sales.paid_ticket_count or 0
        result[site]['unpaid_revenue'] = float(sales.unpaid_revenue) if sales.unpaid_revenue else 0
        result[site]['unpaid_ticket_count'] = sales.unpaid_ticket_count or 0
        
        # 등급별 매수 (PerformanceDailySalesGrade 모델에서 가져오기)
        for grade_sales in sales.grade_sales.all():
            seat_grade_name = grade_sales.seat_grade.name
            if grade_sales.paid_count > 0:
                result[site]['paid_by_grade'][seat_grade_name] = grade_sales.paid_count
            if grade_sales.unpaid_count > 0:
                result[site]['unpaid_by_grade'][seat_grade_name] = grade_sales.unpaid_count
            if grade_sales.free_count > 0:
                result[site]['free_by_grade'][seat_grade_name] = grade_sales.free_count
    
    return JsonResponse({'success': True, 'data': result})
