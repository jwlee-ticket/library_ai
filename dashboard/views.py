from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Min, Max, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from collections import defaultdict
from performance.models import Performance
from data_management.models import PerformanceDailySales, PerformanceDailySalesGrade


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
    """공연별 대시보드 상세 뷰 (장르별로 다른 템플릿 사용)"""
    model = Performance
    context_object_name = 'performance'
    
    def get_template_names(self):
        """장르에 따라 다른 템플릿 반환"""
        performance = self.get_object()
        genre = performance.genre
        
        # 장르별 템플릿 경로 매핑
        genre_template_map = {
            'concert': 'dashboard/concert/detail.html',
            'theater': 'dashboard/theater/detail.html',
            'musical': 'dashboard/musical/detail.html',
            'exhibition': 'dashboard/exhibition/detail.html',
        }
        
        # 장르별 템플릿이 있으면 사용, 없으면 기본 템플릿 사용
        return [genre_template_map.get(genre, 'dashboard/detail.html')]


class ConcertOverviewDashboardView(TemplateView):
    """콘서트 통합 대시보드 뷰"""
    template_name = 'dashboard/concert/overview.html'


@login_required
@require_http_methods(["GET"])
def get_concert_aggregated_summary_data(request):
    """콘서트 통합 대시보드 요약 데이터 API"""
    try:
        # 모든 콘서트 공연 조회
        concerts = Performance.objects.filter(genre='concert')
        
        if not concerts.exists():
            return JsonResponse({
                'success': True,
                'data': {
                    'total_revenue': 0,
                    'total_ticket_count': 0,
                    'today_revenue': 0,
                    'today_ticket_count': 0,
                }
            })
        
        # 오늘 날짜
        today = datetime.now().date()
        
        ignore_booking_sites = ['미', '미지정', '합계', 'TOTAL', '계', '전체', '총계', '유료 계', '초대']

        # 모든 콘서트의 일일 매출 데이터 조회
        all_daily_sales = PerformanceDailySales.objects.filter(
            performance__genre='concert'
        ).exclude(
            booking_site__name__in=ignore_booking_sites
        )
        
        # 총 매출 계산 (모든 날짜의 모든 콘서트)
        total_revenue_result = all_daily_sales.aggregate(
            total_paid=Sum('paid_revenue'),
            total_unpaid=Sum('unpaid_revenue')
        )
        total_revenue = float(total_revenue_result['total_paid'] or 0) + float(total_revenue_result['total_unpaid'] or 0)
        
        # 총 판매 매수 계산 (모든 날짜의 모든 콘서트)
        total_ticket_result = all_daily_sales.aggregate(
            total_paid_tickets=Sum('paid_ticket_count'),
            total_unpaid_tickets=Sum('unpaid_ticket_count')
        )
        total_ticket_count = (total_ticket_result['total_paid_tickets'] or 0) + (total_ticket_result['total_unpaid_tickets'] or 0)
        
        # 오늘 매출 계산
        today_sales = all_daily_sales.filter(date=today)
        today_revenue_result = today_sales.aggregate(
            total_paid=Sum('paid_revenue'),
            total_unpaid=Sum('unpaid_revenue')
        )
        today_revenue = float(today_revenue_result['total_paid'] or 0) + float(today_revenue_result['total_unpaid'] or 0)
        
        # 오늘 판매 매수 계산
        today_ticket_result = today_sales.aggregate(
            total_paid_tickets=Sum('paid_ticket_count'),
            total_unpaid_tickets=Sum('unpaid_ticket_count')
        )
        today_ticket_count = (today_ticket_result['total_paid_tickets'] or 0) + (today_ticket_result['total_unpaid_tickets'] or 0)
        
        # 총 목표 매출 계산 (모든 콘서트의 target_revenue 합계)
        total_target_revenue = 0
        for concert in concerts:
            if concert.target_revenue:
                total_target_revenue += float(concert.target_revenue)
        
        # 총 손익분기점 계산 (모든 콘서트의 break_even_point 합계)
        total_break_even_point = 0
        for concert in concerts:
            if concert.break_even_point:
                total_break_even_point += float(concert.break_even_point)
        
        # 총 오픈 판매 매수 계산 (모든 콘서트의 seat_grades 합계)
        total_seats = 0
        for concert in concerts:
            for seat_grade in concert.seat_grades.all():
                total_seats += seat_grade.seat_count
        
        # 개별 콘서트 목록 데이터
        concert_list = []
        for concert in concerts:
            # 각 콘서트의 총 매출 계산
            concert_sales = PerformanceDailySales.objects.filter(performance=concert)
            concert_revenue_result = concert_sales.aggregate(
                total_paid=Sum('paid_revenue'),
                total_unpaid=Sum('unpaid_revenue')
            )
            concert_revenue = float(concert_revenue_result['total_paid'] or 0) + float(concert_revenue_result['total_unpaid'] or 0)
            
            # 목표액
            target_revenue = float(concert.target_revenue) if concert.target_revenue else 0
            
            # 달성율 계산
            achievement_rate = 0
            if target_revenue > 0:
                achievement_rate = (concert_revenue / target_revenue) * 100
            
            concert_list.append({
                'id': concert.id,
                'title': concert.title,
                'target_revenue': target_revenue,
                'total_revenue': concert_revenue,
                'achievement_rate': achievement_rate,
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_revenue': total_revenue,
                'total_ticket_count': total_ticket_count,
                'today_revenue': today_revenue,
                'today_ticket_count': today_ticket_count,
                'total_target_revenue': total_target_revenue,
                'total_break_even_point': total_break_even_point,
                'total_seats': total_seats,
                'concert_list': concert_list,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_concert_period_revenue_data(request):
    """콘서트 통합 대시보드 기간별 매출 데이터 API"""
    try:
        # 파라미터
        period_type = request.GET.get('period_type', 'daily')  # daily, weekly, monthly
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        # 기본값 설정
        today = datetime.now().date()
        if not start_date_str or not end_date_str:
            if period_type == 'daily':
                end_date = today
                start_date = end_date - timedelta(days=29)  # 최근 30일
            elif period_type == 'weekly':
                end_date = today
                start_date = end_date - timedelta(weeks=3, days=end_date.weekday())  # 최근 4주
            else:  # monthly
                end_date = today
                # 최근 3개월 (현재 월 포함)
                if today.month >= 3:
                    start_date = today.replace(month=today.month - 2, day=1)
                else:
                    start_date = today.replace(year=today.year - 1, month=12 + today.month - 2, day=1)
        else:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'error': '올바른 날짜 형식이 아니에요'}, status=400)
        
        # 모든 콘서트 조회
        concerts = Performance.objects.filter(genre='concert').order_by('id')
        concert_dict = {concert.id: concert.title for concert in concerts}
        
        # 일일 매출 데이터 조회
        daily_sales = PerformanceDailySales.objects.filter(
            performance__genre='concert',
            date__gte=start_date,
            date__lte=end_date
        ).select_related('performance')
        
        # 기간별로 데이터 그룹화
        period_data = defaultdict(lambda: defaultdict(float))
        
        for sale in daily_sales:
            sale_date = sale.date
            performance_id = sale.performance.id
            revenue = float(sale.paid_revenue or 0) + float(sale.unpaid_revenue or 0)
            
            if period_type == 'daily':
                period_key = sale_date.strftime('%Y-%m-%d')
            elif period_type == 'weekly':
                # 주 시작일 계산 (월요일)
                week_start = sale_date - timedelta(days=sale_date.weekday())
                period_key = week_start.strftime('%Y-%m-%d')
            else:  # monthly
                period_key = sale_date.strftime('%Y-%m')
            
            period_data[period_key][performance_id] += revenue
        
        # 기간 목록 정렬
        periods = sorted(period_data.keys())
        
        # 공연 목록
        performances = [{'id': cid, 'title': title} for cid, title in concert_dict.items()]
        
        # 데이터 형식 변환
        data = {}
        for period_key in periods:
            data[period_key] = dict(period_data[period_key])
        
        return JsonResponse({
            'success': True,
            'data': {
                'periods': periods,
                'performances': performances,
                'data': data,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_concert_dashboard_data(request, pk):
    """공연별 대시보드 데이터 API"""
    performance = get_object_or_404(Performance, id=pk)
    
    # 날짜 범위 파라미터
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    ignore_booking_sites = ['미', '미지정', '합계', 'TOTAL', '계', '전체', '총계', '유료 계', '초대']

    if not start_date_str or not end_date_str:
        sales_date_range = PerformanceDailySales.objects.filter(
            performance=performance
        ).exclude(
            booking_site__name__in=ignore_booking_sites
        ).aggregate(
            min_date=Min('date'),
            max_date=Max('date')
        )
        grade_date_range = PerformanceDailySalesGrade.objects.filter(
            daily_sales__performance=performance
        ).aggregate(
            min_date=Min('daily_sales__date'),
            max_date=Max('daily_sales__date')
        )

        min_candidates = [sales_date_range['min_date'], grade_date_range['min_date']]
        max_candidates = [sales_date_range['max_date'], grade_date_range['max_date']]
        min_candidates = [value for value in min_candidates if value]
        max_candidates = [value for value in max_candidates if value]

        if min_candidates and max_candidates:
            start_date = min(min_candidates)
            end_date = max(max_candidates)
        else:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': '올바른 날짜 형식이 아니에요'}, status=400)
    
    # 매출 데이터 조회
    sales_data = PerformanceDailySales.objects.filter(
        performance=performance,
        date__gte=start_date,
        date__lte=end_date
    ).exclude(
        booking_site__name__in=ignore_booking_sites
    ).order_by('date', 'booking_site')
    
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    # 예매처 목록 (실제 데이터에서 추출)
    booking_site_set = set()
    for sale in sales_data.select_related('booking_site'):
        if sale.booking_site:
            booking_site_set.add(sale.booking_site.name)
    booking_site_set.update(performance.booking_sites.values_list('name', flat=True))
    booking_sites = sorted({name for name in booking_site_set if name not in ignore_booking_sites})
    
    # 날짜별, 예매처별, 입금/미입금별로 데이터 정리
    daily_revenue_data = {}  # {date: {site: {paid: 0, unpaid: 0}}}
    daily_ticket_data = {}   # {date: {site: {paid: 0, unpaid: 0}}}

    # 초기화: 모든 날짜와 예매처 조합을 0으로 초기화
    for date_str in date_list:
        daily_revenue_data[date_str] = {}
        daily_ticket_data[date_str] = {}
        for site in booking_sites:
            daily_revenue_data[date_str][site] = {'paid': 0, 'unpaid': 0}
            daily_ticket_data[date_str][site] = {'paid': 0, 'unpaid': 0}

    # 실제 데이터 채우기
    for sale in sales_data:
        date_str = sale.date.strftime('%Y-%m-%d')
        site = sale.booking_site.name if sale.booking_site else '미지정'
        
        if date_str not in daily_revenue_data:
            daily_revenue_data[date_str] = {}
            daily_ticket_data[date_str] = {}
        
        if site not in daily_revenue_data[date_str]:
            daily_revenue_data[date_str][site] = {'paid': 0, 'unpaid': 0}
            daily_ticket_data[date_str][site] = {'paid': 0, 'unpaid': 0}
        
        # Decimal을 float으로 변환
        daily_revenue_data[date_str][site]['paid'] += float(sale.paid_revenue) if sale.paid_revenue else 0
        daily_revenue_data[date_str][site]['unpaid'] += float(sale.unpaid_revenue) if sale.unpaid_revenue else 0
        daily_ticket_data[date_str][site]['paid'] += sale.paid_ticket_count or 0
        daily_ticket_data[date_str][site]['unpaid'] += sale.unpaid_ticket_count or 0
    
    # 총 좌석수 계산 (seat_grades 모델에서 합산)
    total_seats = 0
    for seat_grade in performance.seat_grades.all():
        total_seats += seat_grade.seat_count
    
    # 목표액, 손익분기점
    target_revenue = float(performance.target_revenue) if performance.target_revenue else None
    break_even_point = float(performance.break_even_point) if performance.break_even_point else None
    
    # 총 매출 계산 (전체 기간)
    paid_total = sales_data.aggregate(total=Sum('paid_revenue'))['total'] or 0
    unpaid_total = sales_data.aggregate(total=Sum('unpaid_revenue'))['total'] or 0
    total_revenue = float(paid_total) + float(unpaid_total)
    
    total_ticket_paid = sales_data.aggregate(total=Sum('paid_ticket_count'))['total'] or 0
    total_ticket_unpaid = sales_data.aggregate(total=Sum('unpaid_ticket_count'))['total'] or 0
    total_ticket_count = total_ticket_paid + total_ticket_unpaid
    
    # 등급별 판매현황 데이터 (PerformanceDailySalesGrade에서 합산)
    grade_sales_data = {}
    grade_sales_qs = PerformanceDailySalesGrade.objects.filter(
        daily_sales__performance=performance,
        daily_sales__date__gte=start_date,
        daily_sales__date__lte=end_date
    ).values(
        'seat_grade__name',
        'seat_grade__seat_count'
    ).annotate(
        paid_count=Sum('paid_count'),
        unpaid_count=Sum('unpaid_count'),
        free_count=Sum('free_count'),
        paid_occupancy_rate=Avg('paid_occupancy_rate'),
        total_occupancy_rate=Avg('total_occupancy_rate')
    )
    
    for row in grade_sales_qs:
        grade_name = row['seat_grade__name']
        seat_count = row['seat_grade__seat_count'] or 0
        paid_count = row['paid_count'] or 0
        unpaid_count = row['unpaid_count'] or 0
        free_count = row['free_count'] or 0
        total_count = paid_count + unpaid_count + free_count
        
        stored_paid_rate = row.get('paid_occupancy_rate')
        stored_total_rate = row.get('total_occupancy_rate')
        if stored_paid_rate is not None:
            paid_occupancy_rate = float(stored_paid_rate)
        else:
            paid_occupancy_rate = paid_count / seat_count if seat_count > 0 else 0
        if stored_total_rate is not None:
            total_occupancy_rate = float(stored_total_rate)
        else:
            total_occupancy_rate = total_count / seat_count if seat_count > 0 else 0
        
        grade_sales_data[grade_name] = {
            'paid_count': paid_count,
            'unpaid_count': unpaid_count,
            'free_count': free_count,
            'paid_occupancy_rate': paid_occupancy_rate,
            'total_occupancy_rate': total_occupancy_rate,
            'total_count': total_count,
        }
    
    # 나머지 섹션은 빈 데이터로 반환 (추후 확장)
    discount_sales_data = {}
    age_gender_sales_data = []
    payment_method_sales_data = {}
    card_sales_data = {}
    sales_channel_sales_data = {}
    region_sales_data = {}
    
    return JsonResponse({
        'success': True,
        'data': {
            'dates': date_list,
            'applied_start_date': start_date.strftime('%Y-%m-%d'),
            'applied_end_date': end_date.strftime('%Y-%m-%d'),
            'booking_sites': booking_sites,
            'daily_revenue': daily_revenue_data,
            'daily_tickets': daily_ticket_data,
            'target_revenue': target_revenue,
            'break_even_point': break_even_point,
            'total_seats': total_seats,
            'total_revenue': total_revenue,
            'total_ticket_count': total_ticket_count,
            'grade_sales': grade_sales_data,
            'discount_sales': discount_sales_data,
            'age_gender_sales': age_gender_sales_data,
            'payment_method_sales': payment_method_sales_data,
            'card_sales': card_sales_data,
            'sales_channel_sales': sales_channel_sales_data,
            'region_sales': region_sales_data,
        }
    })
