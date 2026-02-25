from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta, date, time
import json
import re
from decimal import Decimal
from io import BytesIO
import pandas as pd
from django.db import transaction
import os
from .models import (
    PerformanceDailySales,
    PerformanceFinalSales,
    PerformanceDailySalesGrade,
    PerformanceSalesUploadLog,
    PerformanceSalesUploadActionLog,
    MusicalEpisodeSales,
)
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


def _get_actor_name(user):
    if user and user.is_authenticated:
        return user.get_username()
    return ''


def _create_sales_upload_action_log(action_type, performance, upload_log, actor):
    PerformanceSalesUploadActionLog.objects.create(
        performance=performance,
        upload_log=upload_log,
        actor=actor if actor and actor.is_authenticated else None,
        actor_name=_get_actor_name(actor),
        original_filename=upload_log.original_filename if upload_log else '',
        action_type=action_type
    )


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
    if '%' in normalized:
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


def _safe_rate(value):
    if value is None:
        return None
    if isinstance(value, (int, float)) and not pd.isna(value):
        return float(value)
    text = _normalize_text(value)
    if not text:
        return None
    text = text.replace('%', '').replace(',', '')
    try:
        rate = float(text)
    except ValueError:
        return None
    if rate > 1:
        rate = rate / 100
    return rate


def _find_report_sheet(sheet_names):
    for name in sheet_names:
        if '판매' in name and '리포트' in name:
            return name
    return None


def _find_section_row(df, keyword):
    for idx in range(len(df)):
        row = df.iloc[idx].tolist()
        row_text = ' '.join(_normalize_text(value) for value in row if _normalize_text(value))
        if keyword in row_text:
            return idx
    return None


def _parse_discount_sales_section(df):
    section_row_idx = _find_section_row(df, '2. 할인권종별 판매현황')
    if section_row_idx is None:
        return {}, 0

    header_row_idx = section_row_idx + 1
    if header_row_idx >= len(df):
        return {}, 0

    header_row = df.iloc[header_row_idx].tolist()
    column_map = {}
    for idx, value in enumerate(header_row):
        label = _normalize_text(value)
        if label in ['구분', '권종명', '매수', '금액']:
            column_map[label] = idx

    if '구분' not in column_map or '권종명' not in column_map or '매수' not in column_map:
        return {}, 0

    booking_site_idx = column_map['구분']
    discount_type_idx = column_map['권종명']
    count_idx = column_map['매수']
    amount_idx = column_map.get('금액')

    discount_sales = {}
    current_site = None
    total_count = 0

    for row_idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[row_idx].tolist()
        row_text = ' '.join(_normalize_text(value) for value in row if _normalize_text(value))
        if not row_text:
            continue
        if '3.' in row_text or '성별' in row_text or '연령' in row_text:
            break

        site_value = _normalize_text(row[booking_site_idx]) if booking_site_idx < len(row) else ''
        if site_value:
            current_site = site_value

        discount_type = _normalize_text(row[discount_type_idx]) if discount_type_idx < len(row) else ''
        if not discount_type or discount_type in ['권종명', '합계', '총계', '계']:
            continue

        if not current_site:
            continue

        sales_count = _safe_int(row[count_idx]) if count_idx < len(row) else 0
        revenue = _safe_int(row[amount_idx]) if amount_idx is not None and amount_idx < len(row) else 0
        if sales_count == 0 and revenue == 0:
            continue

        discount_sales.setdefault(current_site, []).append({
            'discount_type': discount_type,
            'sales_count': sales_count,
            'revenue': revenue
        })
        total_count += 1

    return discount_sales, total_count


def _parse_age_gender_sales_section(df):
    section_row_idx = _find_section_row(df, '3. 성별, 연령대별 판매현황')
    if section_row_idx is None:
        return [], 0

    header_row_idx = section_row_idx + 1
    if header_row_idx >= len(df):
        return [], 0

    header_row = df.iloc[header_row_idx].tolist()
    column_map = {}
    for idx, value in enumerate(header_row):
        label = _normalize_text(value)
        if label in ['연령대', '남', '녀', '성별모름', '계']:
            column_map[label] = idx

    if '연령대' not in column_map:
        return [], 0

    age_idx = column_map['연령대']
    male_idx = column_map.get('남')
    female_idx = column_map.get('녀')
    unknown_idx = column_map.get('성별모름')
    total_idx = column_map.get('계')

    age_gender_sales = []
    total_count = 0

    for row_idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[row_idx].tolist()
        row_text = ' '.join(_normalize_text(value) for value in row if _normalize_text(value))
        if not row_text:
            continue
        if '4.' in row_text or '결제수단' in row_text:
            break

        age_group = _normalize_text(row[age_idx]) if age_idx < len(row) else ''
        if not age_group or age_group in ['연령대', '계', '총계']:
            continue

        male_count = _safe_int(row[male_idx]) if male_idx is not None and male_idx < len(row) else 0
        female_count = _safe_int(row[female_idx]) if female_idx is not None and female_idx < len(row) else 0
        unknown_count = _safe_int(row[unknown_idx]) if unknown_idx is not None and unknown_idx < len(row) else 0
        total = _safe_int(row[total_idx]) if total_idx is not None and total_idx < len(row) else (male_count + female_count + unknown_count)

        if male_count == 0 and female_count == 0 and unknown_count == 0 and total == 0:
            continue

        age_gender_sales.append({
            'age_group': age_group,
            'male_count': male_count,
            'female_count': female_count,
            'unknown_count': unknown_count,
            'total_count': total
        })
        total_count += 1

    return age_gender_sales, total_count


def _parse_payment_method_sales_section(df):
    section_row_idx = _find_section_row(df, '4. 결제수단별 판매현황')
    if section_row_idx is None:
        return {}, 0

    header_row_idx = section_row_idx + 1
    if header_row_idx >= len(df):
        return {}, 0

    header_row = df.iloc[header_row_idx].tolist()
    normalized_headers = [_normalize_text(value) for value in header_row]

    payment_method_idx = None
    for idx, label in enumerate(normalized_headers):
        if label == '결제수단':
            payment_method_idx = idx
            break

    if payment_method_idx is None:
        return {}, 0

    count_idx = None
    amount_idx = None
    for idx in range(payment_method_idx + 1, len(normalized_headers)):
        label = normalized_headers[idx]
        if label == '매수' and count_idx is None:
            count_idx = idx
            continue
        if label == '금액' and amount_idx is None:
            amount_idx = idx
        if count_idx is not None and amount_idx is not None:
            break

    if count_idx is None:
        return {}, 0

    payment_method_sales = {}
    total_count = 0

    for row_idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[row_idx].tolist()
        row_text = ' '.join(_normalize_text(value) for value in row if _normalize_text(value))
        if not row_text:
            continue
        if '6.' in row_text or '판매경로' in row_text:
            break

        method_name = _normalize_text(row[payment_method_idx]) if payment_method_idx < len(row) else ''
        if not method_name or method_name in ['결제수단', '계', '총계']:
            continue

        count = _safe_int(row[count_idx]) if count_idx < len(row) else 0
        amount = _safe_int(row[amount_idx]) if amount_idx is not None and amount_idx < len(row) else 0
        if count == 0 and amount == 0:
            continue

        payment_method_sales.setdefault(method_name, {'count': 0, 'amount': 0})
        payment_method_sales[method_name]['count'] += count
        payment_method_sales[method_name]['amount'] += amount
        total_count += 1

    return payment_method_sales, total_count


def _parse_card_sales_section(df):
    section_row_idx = _find_section_row(df, '5.카드별 매출집계')
    if section_row_idx is None:
        section_row_idx = _find_section_row(df, '5. 카드별 매출집계')
    if section_row_idx is None:
        return {}, 0

    header_row_idx = section_row_idx + 1
    if header_row_idx >= len(df):
        return {}, 0

    header_row = df.iloc[header_row_idx].tolist()
    normalized_headers = [_normalize_text(value) for value in header_row]

    card_name_indices = [idx for idx, label in enumerate(normalized_headers) if label == '결제수단']
    if not card_name_indices:
        return {}, 0
    # 카드별 매출집계는 오른쪽 블록(두 번째 결제수단)을 사용
    card_name_idx = card_name_indices[-1]

    count_idx = None
    amount_idx = None
    for idx in range(card_name_idx + 1, len(normalized_headers)):
        label = normalized_headers[idx]
        if label == '매수' and count_idx is None:
            count_idx = idx
            continue
        if label == '금액' and amount_idx is None:
            amount_idx = idx
        if count_idx is not None and amount_idx is not None:
            break

    if count_idx is None:
        return {}, 0

    card_sales = {}
    total_count = 0

    for row_idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[row_idx].tolist()
        row_text = ' '.join(_normalize_text(value) for value in row if _normalize_text(value))
        if not row_text:
            continue
        if '6.' in row_text or '판매경로' in row_text:
            break

        card_name = _normalize_text(row[card_name_idx]) if card_name_idx < len(row) else ''
        if not card_name or card_name in ['결제수단', '계', '총계']:
            continue

        count = _safe_int(row[count_idx]) if count_idx < len(row) else 0
        amount = _safe_int(row[amount_idx]) if amount_idx is not None and amount_idx < len(row) else 0
        if count == 0 and amount == 0:
            continue

        card_sales.setdefault(card_name, {'count': 0, 'amount': 0})
        card_sales[card_name]['count'] += count
        card_sales[card_name]['amount'] += amount
        total_count += 1

    return card_sales, total_count


def _parse_sales_channel_section(df):
    section_row_idx = _find_section_row(df, '6. 판매경로별 판매현황')
    if section_row_idx is None:
        return [], 0

    header_row_idx = section_row_idx + 1
    if header_row_idx >= len(df):
        return [], 0

    header_row = df.iloc[header_row_idx].tolist()
    column_map = {}
    for idx, value in enumerate(header_row):
        label = _normalize_text(value)
        if label in ['판매경로', '매수', '금액']:
            column_map[label] = idx

    if '판매경로' not in column_map or '매수' not in column_map:
        return [], 0

    channel_idx = column_map['판매경로']
    count_idx = column_map['매수']
    amount_idx = column_map.get('금액')

    sales_channels = []
    total_count = 0

    for row_idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[row_idx].tolist()
        row_text = ' '.join(_normalize_text(value) for value in row if _normalize_text(value))
        if not row_text:
            continue
        if '7.' in row_text or '지역' in row_text:
            break

        channel = _normalize_text(row[channel_idx]) if channel_idx < len(row) else ''
        if not channel or channel in ['판매경로', '계', '총계']:
            continue

        count = _safe_int(row[count_idx]) if count_idx < len(row) else 0
        amount = _safe_int(row[amount_idx]) if amount_idx is not None and amount_idx < len(row) else 0
        if count == 0 and amount == 0:
            continue

        sales_channels.append({
            'sales_channel': channel,
            'count': count,
            'amount': amount
        })
        total_count += 1

    return sales_channels, total_count


def _parse_region_sales_section(df):
    section_row_idx = _find_section_row(df, '7. 지역별 판매현황')
    if section_row_idx is None:
        return [], 0

    header_row_idx = section_row_idx + 2
    if header_row_idx >= len(df):
        return [], 0

    header_row = df.iloc[header_row_idx].tolist()
    normalized_headers = [_normalize_text(value) for value in header_row]

    group_starts = []
    for idx, label in enumerate(normalized_headers):
        if label and label.endswith('지역별'):
            group_starts.append((idx, label))
        elif label == '지역' and not group_starts:
            group_starts.append((idx, '지역별'))

    if not group_starts:
        return [], 0

    def _find_count_index(start_idx):
        for idx in range(start_idx + 1, len(normalized_headers)):
            if normalized_headers[idx] == '매수':
                return idx
        return None

    groups = []
    for start_idx, title in group_starts:
        count_idx = _find_count_index(start_idx)
        groups.append({
            'title': title,
            'start_idx': start_idx,
            'count_idx': count_idx,
            'rows': []
        })

    total_count = 0

    for row_idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[row_idx].tolist()
        row_text = ' '.join(_normalize_text(value) for value in row if _normalize_text(value))
        if not row_text:
            continue

        for group in groups:
            start_idx = group['start_idx']
            count_idx = group['count_idx']
            if start_idx is None or start_idx >= len(row):
                continue
            region_name = _normalize_text(row[start_idx])
            if not region_name or region_name in ['지역', '계', '총계', group['title']]:
                continue
            region_count = _safe_int(row[count_idx]) if count_idx is not None and count_idx < len(row) else 0
            if region_count <= 0:
                continue
            group['rows'].append({'region': region_name, 'count': region_count})
            total_count += 1

    region_groups = [
        {'title': group['title'], 'rows': group['rows']}
        for group in groups
        if group['rows']
    ]
    return region_groups, total_count


def _parse_final_sales_excel(xls, report_sheet):
    df = pd.read_excel(xls, sheet_name=report_sheet, header=None)
    discount_sales, discount_sales_count = _parse_discount_sales_section(df)
    age_gender_sales, age_gender_count = _parse_age_gender_sales_section(df)
    payment_method_sales, payment_method_count = _parse_payment_method_sales_section(df)
    card_sales, card_sales_count = _parse_card_sales_section(df)
    sales_channel_sales, sales_channel_count = _parse_sales_channel_section(df)
    region_groups, region_sales_count = _parse_region_sales_section(df)
    return {
        'discount_sales': discount_sales,
        'discount_sales_count': discount_sales_count,
        'age_gender_sales': age_gender_sales,
        'age_gender_sales_count': age_gender_count,
        'payment_method_sales': payment_method_sales,
        'payment_method_sales_count': payment_method_count,
        'card_sales': card_sales,
        'card_sales_count': card_sales_count,
        'sales_channel_sales': sales_channel_sales,
        'sales_channel_sales_count': sales_channel_count,
        'region_sales_groups': region_groups,
        'region_sales_count': region_sales_count,
        'sheet_name': report_sheet
    }


def _parse_date(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return pd.to_datetime(value).date()
    except ValueError:
        return None


def _parse_excel_serial_date(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)):
        try:
            return (datetime(1899, 12, 30) + timedelta(days=float(value))).date()
        except (ValueError, OverflowError):
            return None
    parsed = _parse_date(value)
    return parsed


def _parse_excel_fraction_time(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return value.time().replace(second=0, microsecond=0)
    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)
    if isinstance(value, (int, float)):
        try:
            total_seconds = int(round((float(value) % 1) * 24 * 60 * 60))
            hour = (total_seconds // 3600) % 24
            minute = (total_seconds % 3600) // 60
            return time(hour=hour, minute=minute)
        except (ValueError, OverflowError):
            return None
    text = _normalize_text(value)
    if not text:
        return None
    for fmt in ['%H:%M', '%H:%M:%S']:
        try:
            return datetime.strptime(text, fmt).time().replace(second=0, microsecond=0)
        except ValueError:
            continue
    return None


def _safe_decimal(value, default='0'):
    text = _normalize_text(value)
    if not text:
        return Decimal(default)
    text = text.replace(',', '')
    try:
        return Decimal(str(float(text))).quantize(Decimal('1'))
    except Exception:
        return Decimal(default)


def _safe_ratio_decimal(value):
    rate = _safe_rate(value)
    if rate is None:
        return None
    return Decimal(str(rate))


def _decrypt_excel_if_needed(excel_file, password=None):
    excel_file.seek(0)
    raw = excel_file.read()
    if not password:
        return BytesIO(raw), False
    try:
        import msoffcrypto
    except Exception as exc:
        raise ValueError('비밀번호 파일 처리를 위한 msoffcrypto-tool 패키지가 필요해요') from exc

    office_file = msoffcrypto.OfficeFile(BytesIO(raw))
    if not office_file.is_encrypted():
        return BytesIO(raw), False

    decrypted_stream = BytesIO()
    try:
        office_file.load_key(password=password)
        office_file.decrypt(decrypted_stream)
    except Exception as exc:
        raise ValueError('엑셀 비밀번호가 올바르지 않거나 복호화에 실패했어요') from exc
    decrypted_stream.seek(0)
    return decrypted_stream, True


def _open_excel_file(file_obj, original_filename=''):
    filename = (original_filename or '').lower()
    if filename.endswith('.xlsb'):
        try:
            import pyxlsb  # noqa: F401
        except Exception as exc:
            raise ValueError('.xlsb 처리를 위한 pyxlsb 패키지가 필요해요') from exc
        return pd.ExcelFile(file_obj, engine='pyxlsb')
    return pd.ExcelFile(file_obj)


def _find_musical_episode_sheet(sheet_names):
    candidates = ['회차별 판매', '회차별판매', 'Episode Sales']
    return next((name for name in candidates if name in sheet_names), None)


def _read_header_tokens(df, header_row_idx, col_idx):
    tokens = []
    for row_offset in [2, 1, 0]:
        idx = header_row_idx - row_offset
        if idx < 0 or idx >= len(df):
            continue
        cell = df.iloc[idx, col_idx] if col_idx < len(df.columns) else None
        text = _normalize_text(cell)
        if text:
            tokens.append(text)
    return tokens


def _build_forward_filled_labels(df, row_idx, col_count):
    if row_idx < 0 or row_idx >= len(df):
        return [''] * col_count
    labels = []
    last_label = ''
    for col_idx in range(col_count):
        cell = df.iloc[row_idx, col_idx] if col_idx < len(df.columns) else None
        label = _normalize_text(cell)
        if label:
            last_label = label
        labels.append(last_label)
    return labels


def _token_has_all(tokens, words):
    joined = ' '.join(tokens)
    return all(word in joined for word in words)


def _parse_musical_episode_sheet(xls, sheet_name):
    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
    header_row_idx = None
    for idx in range(min(20, len(df))):
        row = [_normalize_text(value) for value in df.iloc[idx].tolist()]
        if any(value in ['No.', 'No'] for value in row) and 'Date' in row and 'Time' in row:
            header_row_idx = idx
            break
    if header_row_idx is None:
        raise ValueError('회차별 판매 시트에서 No./Date/Time 헤더를 찾을 수 없어요')

    col_count = len(df.columns)
    no_idx = date_idx = day_idx = time_idx = None
    remark_indices = []
    paid_count_idx = paid_rate_idx = paid_revenue_idx = None
    unpaid_count_idx = unpaid_rate_idx = unpaid_revenue_idx = None
    invited_count_idx = invited_rate_idx = None
    total_paid_count_idx = total_paid_rate_idx = None

    header_labels = [_normalize_text(df.iloc[header_row_idx, col]) for col in range(col_count)]
    group_labels = _build_forward_filled_labels(df, header_row_idx - 1, col_count)

    for col_idx, label in enumerate(header_labels):
        if label in ['No.', 'No']:
            no_idx = col_idx
        elif label == 'Date':
            date_idx = col_idx
        elif label == 'Day':
            day_idx = col_idx
        elif label == 'Time':
            time_idx = col_idx
        elif label in ['비고', 'Remark'] or '비고' in group_labels[col_idx]:
            remark_indices.append(col_idx)
    if remark_indices:
        explicit_remark_indices = [idx for idx in remark_indices if header_labels[idx] in ['비고', 'Remark']]
        if explicit_remark_indices:
            remark_indices = [explicit_remark_indices[0]]
        else:
            # 비고 그룹이 여러 컬럼이면 왼쪽 첫 컬럼을 우선 사용
            remark_indices = [min(remark_indices)]


    if no_idx is None or date_idx is None or time_idx is None:
        raise ValueError('회차별 판매 시트에서 필수 컬럼(No./Date/Time)을 찾을 수 없어요')

    for col_idx in range(col_count):
        tokens = _read_header_tokens(df, header_row_idx, col_idx)
        if not tokens:
            continue
        group_label = group_labels[col_idx]
        label = header_labels[col_idx]

        if paid_count_idx is None and '유료' in group_label and '입금' in group_label and label in ['수량', '매수']:
            paid_count_idx = col_idx
        elif paid_rate_idx is None and '유료' in group_label and '입금' in group_label and label in ['%', '비율']:
            paid_rate_idx = col_idx
        elif paid_revenue_idx is None and '유료' in group_label and '입금' in group_label and label == '금액':
            paid_revenue_idx = col_idx
        elif unpaid_count_idx is None and '유료' in group_label and '미입금' in group_label and label in ['수량', '매수']:
            unpaid_count_idx = col_idx
        elif unpaid_rate_idx is None and '유료' in group_label and '미입금' in group_label and label in ['%', '비율']:
            unpaid_rate_idx = col_idx
        elif unpaid_revenue_idx is None and '유료' in group_label and '미입금' in group_label and label == '금액':
            unpaid_revenue_idx = col_idx
        elif invited_count_idx is None and '초대' in group_label and label in ['수량', '매수']:
            invited_count_idx = col_idx
        elif invited_rate_idx is None and '초대' in group_label and label in ['%', '비율']:
            invited_rate_idx = col_idx
        elif total_paid_count_idx is None and '합계' in group_label and '입금' in group_label and label in ['수량', '매수']:
            total_paid_count_idx = col_idx
        elif total_paid_rate_idx is None and '합계' in group_label and '입금' in group_label and label in ['%', '비율']:
            total_paid_rate_idx = col_idx

    cast_columns = []
    for col_idx, group_label in enumerate(group_labels):
        if 'CAST' in group_label.upper():
            cast_name = header_labels[col_idx]
            if cast_name and cast_name not in ['No.', 'No', 'Date', 'Day', 'Time']:
                cast_columns.append((col_idx, cast_name))

    if not cast_columns:
        cast_start_idx = time_idx + 1
        cast_end_idx = remark_idx if remark_idx is not None else col_count
        metric_candidates = [idx for idx in [
            paid_count_idx, paid_rate_idx, paid_revenue_idx,
            unpaid_count_idx, unpaid_rate_idx, unpaid_revenue_idx,
            invited_count_idx, invited_rate_idx,
            total_paid_count_idx, total_paid_rate_idx,
        ] if idx is not None]
        if metric_candidates:
            cast_end_idx = min(cast_end_idx, min(metric_candidates))
        else:
            metric_stop_keywords = ['유료', '입금', '미입금', '초대', '합계', '비고']
            for col_idx in range(cast_start_idx, col_count):
                label = header_labels[col_idx]
                group_label = group_labels[col_idx]
                if label in ['수량', '매수', '금액', '%', '비율'] or any(word in group_label for word in metric_stop_keywords):
                    cast_end_idx = min(cast_end_idx, col_idx)
                    break

        for col_idx in range(cast_start_idx, max(cast_start_idx, cast_end_idx)):
            cast_name = _normalize_text(df.iloc[header_row_idx, col_idx])
            if cast_name:
                cast_columns.append((col_idx, cast_name))

    rows = []
    max_no = 0
    for row_idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[row_idx].tolist()
        episode_no = _safe_int(row[no_idx]) if no_idx < len(row) else 0
        if episode_no <= 0:
            continue

        show_date = _parse_excel_serial_date(row[date_idx] if date_idx < len(row) else None)
        if not show_date:
            continue

        cast_map = {}
        for col_idx, cast_name in cast_columns:
            if col_idx >= len(row):
                continue
            cast_value = _normalize_text(row[col_idx])
            if cast_value:
                cast_map[cast_name] = cast_value

        row_data = {
            'episode_no': episode_no,
            'show_date': show_date,
            'show_day': _normalize_text(row[day_idx]) if day_idx is not None and day_idx < len(row) else '',
            'show_time': _parse_excel_fraction_time(row[time_idx]) if time_idx < len(row) else None,
            'cast_map': cast_map,
            'paid_ticket_count': _safe_int(row[paid_count_idx]) if paid_count_idx is not None and paid_count_idx < len(row) else 0,
            'paid_rate': _safe_ratio_decimal(row[paid_rate_idx]) if paid_rate_idx is not None and paid_rate_idx < len(row) else None,
            'paid_revenue': _safe_decimal(row[paid_revenue_idx]) if paid_revenue_idx is not None and paid_revenue_idx < len(row) else Decimal('0'),
            'unpaid_ticket_count': _safe_int(row[unpaid_count_idx]) if unpaid_count_idx is not None and unpaid_count_idx < len(row) else 0,
            'unpaid_rate': _safe_ratio_decimal(row[unpaid_rate_idx]) if unpaid_rate_idx is not None and unpaid_rate_idx < len(row) else None,
            'unpaid_revenue': _safe_decimal(row[unpaid_revenue_idx]) if unpaid_revenue_idx is not None and unpaid_revenue_idx < len(row) else Decimal('0'),
            'invited_ticket_count': _safe_int(row[invited_count_idx]) if invited_count_idx is not None and invited_count_idx < len(row) else 0,
            'invited_rate': _safe_ratio_decimal(row[invited_rate_idx]) if invited_rate_idx is not None and invited_rate_idx < len(row) else None,
            'total_paid_ticket_count': _safe_int(row[total_paid_count_idx]) if total_paid_count_idx is not None and total_paid_count_idx < len(row) else 0,
            'total_paid_rate': _safe_ratio_decimal(row[total_paid_rate_idx]) if total_paid_rate_idx is not None and total_paid_rate_idx < len(row) else None,
            'remark': '',
        }
        if remark_indices:
            remark_texts = []
            for remark_idx in remark_indices:
                if remark_idx >= len(row):
                    continue
                remark_text = _normalize_text(row[remark_idx])
                if not remark_text:
                    continue
                # 숫자 전용 값은 비고 텍스트로 보지 않음
                if re.fullmatch(r'[0-9,.\s]+', remark_text):
                    continue
                remark_texts.append(remark_text)
            row_data['remark'] = ' / '.join(remark_texts)

        rows.append(row_data)
        if episode_no > max_no:
            max_no = episode_no

    if not rows:
        raise ValueError('회차별 판매 시트에서 숫자 No. 행 데이터를 찾을 수 없어요')
    return rows, {'max_no': max_no, 'sheet_name': sheet_name}


def _save_musical_episode_rows(performance, upload_log, rows, max_no):
    MusicalEpisodeSales.objects.filter(
        performance=performance,
        episode_no__lte=max_no
    ).delete()

    instances = [
        MusicalEpisodeSales(
            performance=performance,
            upload_log=upload_log,
            episode_no=row['episode_no'],
            show_date=row['show_date'],
            show_day=row['show_day'],
            show_time=row['show_time'],
            cast_map=row['cast_map'],
            paid_ticket_count=row['paid_ticket_count'],
            paid_rate=row['paid_rate'],
            paid_revenue=row['paid_revenue'],
            unpaid_ticket_count=row['unpaid_ticket_count'],
            unpaid_rate=row['unpaid_rate'],
            unpaid_revenue=row['unpaid_revenue'],
            invited_ticket_count=row['invited_ticket_count'],
            invited_rate=row['invited_rate'],
            total_paid_ticket_count=row['total_paid_ticket_count'],
            total_paid_rate=row['total_paid_rate'],
            remark=row['remark'],
        )
        for row in rows if row['episode_no'] <= max_no
    ]
    MusicalEpisodeSales.objects.bulk_create(instances, batch_size=500)
    return {'saved_count': len(instances)}


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


def _parse_daily_sales_sheet(xls, sheet_name):
    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)

    header_row_idx = None
    for idx in range(min(10, len(df))):
        if any(_normalize_text(value) == 'DATE' for value in df.iloc[idx].tolist()):
            header_row_idx = idx
            break
    if header_row_idx is None:
        raise ValueError('일일 판매 시트에서 DATE 헤더를 찾을 수 없어요')

    group_row_raw = df.iloc[header_row_idx].tolist()
    sub_row = df.iloc[header_row_idx + 1].tolist()

    group_row = []
    last_label = ''
    for value in group_row_raw:
        label = _normalize_text(value)
        if label:
            last_label = label
        group_row.append(last_label)

    date_idx = None
    for idx, value in enumerate(group_row_raw):
        if _normalize_text(value) == 'DATE':
            date_idx = idx
            break
    if date_idx is None:
        raise ValueError('일일 판매 시트에서 DATE 컬럼을 찾을 수 없어요')

    booking_site_columns = {}
    for idx, (group_label, sub_label) in enumerate(zip(group_row, sub_row)):
        group_label = _normalize_text(group_label)
        sub_label = _normalize_text(sub_label)
        if not group_label or group_label == 'DATE':
            continue

        if group_label in ['초대', '합계']:
            booking_site_columns.setdefault(group_label, {})
            booking_site_columns[group_label]['count'] = idx
            continue

        if sub_label not in ['매수', '금액']:
            continue

        booking_site_columns.setdefault(group_label, {})
        if sub_label == '매수':
            booking_site_columns[group_label]['count'] = idx
        elif sub_label == '금액':
            booking_site_columns[group_label]['amount'] = idx

    daily_sales = {}
    dates_in_file = set()
    active_sites = set()

    for row_idx in range(header_row_idx + 2, len(df)):
        row = df.iloc[row_idx].tolist()
        date_value = row[date_idx]
        normalized_date = _normalize_text(date_value)
        if not normalized_date or _is_summary_row(normalized_date):
            continue

        parsed_date = _parse_date(date_value)
        if not parsed_date:
            continue

        dates_in_file.add(parsed_date)
        daily_sales.setdefault(parsed_date, {})

        for booking_site, columns in booking_site_columns.items():
            count_col = columns.get('count')
            amount_col = columns.get('amount')
            count = _safe_int(row[count_col]) if count_col is not None else 0
            amount = _safe_int(row[amount_col]) if amount_col is not None else 0

            if booking_site not in ['유료 계', '합계', '초대'] and count == 0 and amount == 0:
                continue

            daily_sales[parsed_date][booking_site] = {
                'count': count,
                'amount': amount,
            }
            if booking_site not in ['유료 계', '합계', '초대']:
                active_sites.add(booking_site)

    return daily_sales, dates_in_file, active_sites


def _parse_seat_details_sheet(xls, sheet_name, excel_file, performance):
    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)

    header_row_idx = None
    for idx in range(min(15, len(df))):
        row = df.iloc[idx].tolist()
        if _normalize_text(row[0]) == 'No.' and _normalize_text(row[1]) == 'Date':
            header_row_idx = idx
            break
    if header_row_idx is None:
        raise ValueError('Seat details 시트에서 No./Date 헤더를 찾을 수 없어요')

    group_row_raw = df.iloc[header_row_idx - 1].tolist() if header_row_idx > 0 else []
    sub_row = df.iloc[header_row_idx].tolist()

    group_row = []
    last_label = ''
    for value in group_row_raw:
        label = _normalize_text(value)
        if label:
            last_label = label
        group_row.append(last_label)

    date_idx = 1
    grade_sales = {}
    seat_grade_names = set()
    
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

    for row_idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[row_idx].tolist()
        date_value = row[date_idx] if date_idx < len(row) else None
        parsed_date = file_date_override or _parse_date(date_value)
        if not parsed_date:
            continue

        grade_sales.setdefault(parsed_date, {})

        for col_idx, (group_label, grade_label) in enumerate(zip(group_row, sub_row)):
            group_label = _normalize_text(group_label)
            grade_label = _normalize_text(grade_label)
            if not group_label or not grade_label:
                continue
            if grade_label in ['Tot', 'TOT', '합계', '총계', '전체']:
                continue
            if not _is_valid_seat_grade_label(grade_label):
                continue

            is_paid_rate = '점유율' in group_label and '유료' in group_label
            is_total_rate = '점유율' in group_label and '객석' in group_label

            if is_paid_rate or is_total_rate:
                rate = _safe_rate(row[col_idx]) if col_idx < len(row) else None
                if rate is None:
                    continue
                seat_grade_names.add(grade_label)
                grade_sales[parsed_date].setdefault(
                    grade_label,
                    {'paid': 0, 'free': 0, 'paid_occupancy_rate': None, 'total_occupancy_rate': None}
                )
                if is_paid_rate:
                    grade_sales[parsed_date][grade_label]['paid_occupancy_rate'] = rate
                if is_total_rate:
                    grade_sales[parsed_date][grade_label]['total_occupancy_rate'] = rate
                continue

            if group_label not in ['유료 계', '초대']:
                continue

            value = _safe_int(row[col_idx]) if col_idx < len(row) else 0
            if value == 0:
                continue

            seat_grade_names.add(grade_label)
            grade_sales[parsed_date].setdefault(
                grade_label,
                {'paid': 0, 'free': 0, 'paid_occupancy_rate': None, 'total_occupancy_rate': None}
            )
            if group_label == '유료 계':
                grade_sales[parsed_date][grade_label]['paid'] += value
            elif group_label == '초대':
                grade_sales[parsed_date][grade_label]['free'] += value

    return grade_sales, seat_grade_names


def _parse_sales_excel(excel_file, performance):
    excel_file.seek(0)
    xls = pd.ExcelFile(excel_file)

    daily_sheet_candidates = ['일일 판매', '일일판매', 'Daily Sales']
    seat_details_candidates = ['Seat details', 'Seat Details']

    daily_sheet = next((name for name in daily_sheet_candidates if name in xls.sheet_names), None)
    if not daily_sheet:
        raise ValueError('일일 판매 시트를 찾을 수 없어요')

    seat_details_sheet = next((name for name in seat_details_candidates if name in xls.sheet_names), None)
    if not seat_details_sheet:
        raise ValueError('Seat details 시트를 찾을 수 없어요')

    daily_sales, dates_in_file, active_sites = _parse_daily_sales_sheet(xls, daily_sheet)
    grade_sales_by_date, seat_grade_names = _parse_seat_details_sheet(
        xls,
        seat_details_sheet,
        excel_file,
        performance
    )

    return {
        'daily_sales': daily_sales,
        'grade_sales': grade_sales_by_date,
        'seat_grade_names': seat_grade_names,
        'dates_in_file': dates_in_file,
        'active_sites': active_sites,
        'sheet_name': f'{daily_sheet} / {seat_details_sheet}',
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
    excel_password = request.POST.get('excel_password', '').strip()
    
    try:
        prepared_excel, _ = _decrypt_excel_if_needed(excel_file, excel_password)
        xls = _open_excel_file(prepared_excel, excel_file.name)
        report_sheet = _find_report_sheet(xls.sheet_names)
        daily_sheet_candidates = ['일일 판매', '일일판매', 'Daily Sales']
        has_daily_sheet = any(name in xls.sheet_names for name in daily_sheet_candidates)
        musical_sheet = _find_musical_episode_sheet(xls.sheet_names)

        if performance.genre == 'musical' and musical_sheet:
            rows, meta = _parse_musical_episode_sheet(xls, musical_sheet)
            max_no = meta.get('max_no') or 0
            sheet_name = meta.get('sheet_name', musical_sheet)
            date_start = min(row['show_date'] for row in rows) if rows else None
            date_end = max(row['show_date'] for row in rows) if rows else None

            with transaction.atomic():
                excel_file.seek(0)
                upload_log = PerformanceSalesUploadLog.objects.create(
                    performance=performance,
                    original_filename=excel_file.name,
                    uploaded_file=excel_file,
                    sheet_name=sheet_name,
                    date_start=date_start,
                    date_end=date_end,
                    daily_sales_count=0,
                    grade_sales_count=0,
                    status='success',
                    message=f'뮤지컬 회차별 데이터 저장 (max_no={max_no})'
                )
                _create_sales_upload_action_log('upload', performance, upload_log, request.user)
                result = _save_musical_episode_rows(performance, upload_log, rows, max_no)

            delete_url = reverse('data_management:performance_sales_upload_log_delete', args=[performance.id, upload_log.id])
            download_url = reverse('data_management:performance_sales_upload_log_download', args=[performance.id, upload_log.id])
            return JsonResponse({
                'success': True,
                'message': '엑셀 업로드가 완료되었습니다.',
                'daily_sales_count': 0,
                'grade_sales_count': 0,
                'date_count': len({row['show_date'] for row in rows}),
                'file_name': excel_file.name,
                'sheet_name': sheet_name,
                'date_start': date_start.strftime('%Y-%m-%d') if date_start else '',
                'date_end': date_end.strftime('%Y-%m-%d') if date_end else '',
                'upload_log_id': upload_log.id,
                'delete_url': delete_url,
                'download_url': download_url,
                'musical_type': 'episode_sales',
                'max_no': max_no,
                'saved_count': result.get('saved_count', 0),
            })
        elif report_sheet and not has_daily_sheet:
            parsed = _parse_final_sales_excel(xls, report_sheet)
        else:
            parsed = _parse_sales_excel(prepared_excel, performance)
    except ValueError as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=400)
    
    if 'daily_sales' not in parsed:
        discount_sales = parsed.get('discount_sales', {})
        discount_sales_count = parsed.get('discount_sales_count', 0)
        age_gender_sales = parsed.get('age_gender_sales', [])
        age_gender_sales_count = parsed.get('age_gender_sales_count', 0)
        payment_method_sales = parsed.get('payment_method_sales', {})
        payment_method_sales_count = parsed.get('payment_method_sales_count', 0)
        card_sales = parsed.get('card_sales', {})
        card_sales_count = parsed.get('card_sales_count', 0)
        sales_channel_sales = parsed.get('sales_channel_sales', [])
        sales_channel_sales_count = parsed.get('sales_channel_sales_count', 0)
        region_sales_groups = parsed.get('region_sales_groups', [])
        region_sales_count = parsed.get('region_sales_count', 0)
        sheet_name = parsed.get('sheet_name', '')

        with transaction.atomic():
            excel_file.seek(0)
            upload_log = PerformanceSalesUploadLog.objects.create(
                performance=performance,
                original_filename=excel_file.name,
                uploaded_file=excel_file,
                sheet_name=sheet_name,
                date_start=None,
                date_end=None,
                daily_sales_count=0,
                grade_sales_count=0,
                status='success',
                message='최종 매출(할인권종별) 데이터 저장'
            )
            _create_sales_upload_action_log('upload', performance, upload_log, request.user)

            final_sales = PerformanceFinalSales.objects.filter(
                performance=performance,
                booking_site__isnull=True
            ).order_by('-updated_at').first()

            if not final_sales:
                final_sales = PerformanceFinalSales.objects.create(
                    performance=performance,
                    booking_site=None,
                    paid_revenue=Decimal(0),
                    paid_ticket_count=0,
                    unpaid_revenue=Decimal(0),
                    unpaid_ticket_count=0
                )

            final_sales.booking_site_discount_sales = discount_sales
            final_sales.age_gender_sales = age_gender_sales
            final_sales.payment_method_sales = payment_method_sales
            final_sales.card_sales_summary = [
                {
                    'card_type': card_type,
                    'count': values.get('count', 0),
                    'amount': values.get('amount', 0)
                }
                for card_type, values in card_sales.items()
            ]
            final_sales.sales_channel_sales = sales_channel_sales
            final_sales.region_sales = region_sales_groups
            final_sales.seoul_region_sales = []
            final_sales.gyeonggi_region_sales = []
            final_sales.save(update_fields=[
                'booking_site_discount_sales',
                'age_gender_sales',
                'payment_method_sales',
                'card_sales_summary',
                'sales_channel_sales',
                'region_sales',
                'seoul_region_sales',
                'gyeonggi_region_sales'
            ])

        delete_url = reverse('data_management:performance_sales_upload_log_delete', args=[performance.id, upload_log.id])
        download_url = reverse('data_management:performance_sales_upload_log_download', args=[performance.id, upload_log.id])
        return JsonResponse({
            'success': True,
            'message': '엑셀 업로드가 완료되었습니다.',
            'daily_sales_count': 0,
            'grade_sales_count': 0,
            'date_count': 0,
            'file_name': excel_file.name,
            'sheet_name': sheet_name,
            'date_start': '',
            'date_end': '',
            'upload_log_id': upload_log.id,
            'delete_url': delete_url,
            'download_url': download_url,
            'final_sales_type': 'discount_sales',
            'discount_sales_count': discount_sales_count,
            'age_gender_sales_count': age_gender_sales_count,
            'payment_method_sales_count': payment_method_sales_count,
            'card_sales_count': card_sales_count,
            'sales_channel_sales_count': sales_channel_sales_count,
            'region_sales_count': region_sales_count,
        })

    daily_sales_data = parsed['daily_sales']
    if not daily_sales_data:
        return JsonResponse({'success': False, 'error': '저장할 매출 데이터가 없어요'}, status=400)
    
    seat_grade_names = parsed['seat_grade_names']
    dates_in_file = parsed['dates_in_file']
    grade_sales_by_date = parsed['grade_sales']
    active_sites = parsed.get('active_sites', set())
    sheet_name = parsed.get('sheet_name', '')

    date_start = min(dates_in_file) if dates_in_file else None
    date_end = max(dates_in_file) if dates_in_file else None
    
    with transaction.atomic():
        excel_file.seek(0)
        upload_log = PerformanceSalesUploadLog.objects.create(
            performance=performance,
            original_filename=excel_file.name,
            uploaded_file=excel_file,
            sheet_name=sheet_name,
            date_start=date_start,
            date_end=date_end,
            daily_sales_count=0,
            grade_sales_count=0,
            status='success',
        )
        _create_sales_upload_action_log('upload', performance, upload_log, request.user)

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
        booking_site_names = set(active_sites)
        for date_value in daily_sales_data.values():
            for booking_site_name in date_value.keys():
                if booking_site_name in ['유료 계', '합계', '초대']:
                    booking_site_names.add(booking_site_name)

        for booking_site_name in booking_site_names:
            booking_site, _ = BookingSite.objects.get_or_create(
                performance=performance,
                name=booking_site_name
            )
            booking_site_map[booking_site_name] = booking_site

        daily_sales_index = {}
        for sale_date, site_data in daily_sales_data.items():
            for booking_site_name, data in site_data.items():
                if booking_site_name not in ['유료 계', '합계', '초대'] and booking_site_name not in booking_site_map:
                    continue
                booking_site = booking_site_map.get(booking_site_name)
                count = data.get('count', 0)
                amount = data.get('amount', 0)
                if booking_site_name not in ['유료 계', '합계', '초대'] and count == 0 and amount == 0:
                    continue

                if booking_site_name == '초대':
                    paid_revenue = 0
                    paid_ticket_count = 0
                    unpaid_revenue = 0
                    unpaid_ticket_count = count
                    notes = {'source': 'daily_sales', 'free_ticket_count': count}
                else:
                    paid_revenue = amount
                    paid_ticket_count = count
                    unpaid_revenue = 0
                    unpaid_ticket_count = 0
                    notes = {'source': 'daily_sales'}

                daily_sales = PerformanceDailySales.objects.create(
                    performance=performance,
                    date=sale_date,
                    booking_site=booking_site,
                    upload_log=upload_log,
                    paid_revenue=Decimal(paid_revenue),
                    paid_ticket_count=paid_ticket_count,
                    unpaid_revenue=Decimal(unpaid_revenue),
                    unpaid_ticket_count=unpaid_ticket_count,
                    notes=json.dumps(notes, ensure_ascii=False)
                )
                daily_sales_count += 1
                daily_sales_index[(sale_date, booking_site_name)] = daily_sales

        if grade_sales_by_date:
            PerformanceDailySalesGrade.objects.filter(
                daily_sales__performance=performance
            ).delete()

        for sale_date, grade_data in grade_sales_by_date.items():
            target_daily_sales = daily_sales_index.get((sale_date, '유료 계')) or daily_sales_index.get((sale_date, '합계'))
            if not target_daily_sales:
                continue
            for grade_name, counts in grade_data.items():
                paid_count = counts.get('paid', 0)
                free_count = counts.get('free', 0)
                paid_occupancy_rate = counts.get('paid_occupancy_rate')
                total_occupancy_rate = counts.get('total_occupancy_rate')
                if paid_count == 0 and free_count == 0:
                    if paid_occupancy_rate is None and total_occupancy_rate is None:
                        continue
                PerformanceDailySalesGrade.objects.create(
                    daily_sales=target_daily_sales,
                    seat_grade=seat_grade_map[grade_name],
                    paid_count=paid_count,
                    unpaid_count=0,
                    free_count=free_count,
                    paid_occupancy_rate=Decimal(str(paid_occupancy_rate)) if paid_occupancy_rate is not None else None,
                    total_occupancy_rate=Decimal(str(total_occupancy_rate)) if total_occupancy_rate is not None else None
                )
                grade_sales_count += 1
    
        upload_log.daily_sales_count = daily_sales_count
        upload_log.grade_sales_count = grade_sales_count
        upload_log.save(update_fields=['daily_sales_count', 'grade_sales_count'])
    delete_url = reverse('data_management:performance_sales_upload_log_delete', args=[performance.id, upload_log.id])
    download_url = reverse('data_management:performance_sales_upload_log_download', args=[performance.id, upload_log.id])
    
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
        'download_url': download_url,
    })


@login_required
@require_http_methods(["POST"])
def delete_sales_upload_log(request, performance_id, log_id):
    """업로드 파일 목록에서 로그 삭제"""
    performance = get_object_or_404(Performance, id=performance_id)
    upload_log = get_object_or_404(PerformanceSalesUploadLog, id=log_id, performance=performance)

    with transaction.atomic():
        # 뮤지컬은 업로드 로그 삭제 시 해당 로그 기반 회차 데이터도 함께 제거
        if performance.genre == 'musical':
            MusicalEpisodeSales.objects.filter(
                performance=performance,
                upload_log=upload_log
            ).delete()

        _create_sales_upload_action_log('delete', performance, upload_log, request.user)
        upload_log.delete()

        # 업로드 로그가 더 이상 없으면 뮤지컬 데이터 전체를 정리
        if performance.genre == 'musical':
            has_remaining_upload_logs = PerformanceSalesUploadLog.objects.filter(
                performance=performance
            ).exists()
            if not has_remaining_upload_logs:
                MusicalEpisodeSales.objects.filter(performance=performance).delete()

    return JsonResponse({'success': True})


@login_required
@require_http_methods(["GET"])
def download_sales_upload_log(request, performance_id, log_id):
    """업로드된 엑셀 파일 다운로드"""
    performance = get_object_or_404(Performance, id=performance_id)
    upload_log = get_object_or_404(PerformanceSalesUploadLog, id=log_id, performance=performance)
    if not upload_log.uploaded_file:
        return JsonResponse({'success': False, 'error': '다운로드할 파일이 없어요'}, status=404)
    try:
        _create_sales_upload_action_log('download', performance, upload_log, request.user)
        return FileResponse(
            upload_log.uploaded_file.open('rb'),
            as_attachment=True,
            filename=upload_log.original_filename
        )
    except FileNotFoundError:
        return JsonResponse({'success': False, 'error': '파일을 찾을 수 없어요'}, status=404)


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
