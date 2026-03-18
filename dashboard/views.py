from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Min, Max, Avg, OuterRef, Subquery
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json
import re
from collections import defaultdict
from performance.models import Performance, MarketingMemo
from data_management.models import PerformanceDailySales, PerformanceDailySalesGrade, PerformanceFinalSales, PerformanceSalesUploadLog, MusicalEpisodeSales


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


class MusicalOverviewDashboardView(TemplateView):
    """뮤지컬 통합 대시보드 뷰"""
    template_name = 'dashboard/musical/overview.html'


class TheaterOverviewDashboardView(TemplateView):
    """연극 통합 대시보드 뷰"""
    template_name = 'dashboard/theater/overview.html'


class OverviewDashboardView(TemplateView):
    """전체 대시보드 뷰 (콘서트·뮤지컬·연극 통합, 연극은 레이아웃만)"""
    template_name = 'dashboard/main.html'


@login_required
@require_http_methods(["GET"])
def get_overall_aggregated_summary_data(request):
    """전체 대시보드 요약 API (콘서트 + 뮤지컬 합산, 연극은 0·레이아웃용)"""
    try:
        today = datetime.now().date()
        ignore_booking_sites = ['미', '미지정', '합계', 'TOTAL', '계', '전체', '총계', '유료 계', '초대']
        concert_date_min = None
        concert_date_max = None
        musical_date_min = None
        musical_date_max = None

        # 콘서트
        concerts = Performance.objects.filter(genre='concert')
        concert_revenue = 0
        concert_tickets = 0
        concert_today_revenue = 0
        concert_today_tickets = 0
        concert_target = 0
        concert_bep = 0
        if concerts.exists():
            all_daily = PerformanceDailySales.objects.filter(
                performance__genre='concert'
            ).exclude(booking_site__name__in=ignore_booking_sites)
            rev = all_daily.aggregate(paid=Sum('paid_revenue'), unpaid=Sum('unpaid_revenue'))
            tkt = all_daily.aggregate(paid=Sum('paid_ticket_count'), unpaid=Sum('unpaid_ticket_count'))
            concert_revenue = float(rev['paid'] or 0) + float(rev['unpaid'] or 0)
            concert_tickets = int(tkt['paid'] or 0) + int(tkt['unpaid'] or 0)
            today_sales = all_daily.filter(date=today)
            today_rev = today_sales.aggregate(paid=Sum('paid_revenue'), unpaid=Sum('unpaid_revenue'))
            today_tkt = today_sales.aggregate(paid=Sum('paid_ticket_count'), unpaid=Sum('unpaid_ticket_count'))
            concert_today_revenue = float(today_rev['paid'] or 0) + float(today_rev['unpaid'] or 0)
            concert_today_tickets = int(today_tkt['paid'] or 0) + int(today_tkt['unpaid'] or 0)
            for c in concerts:
                if c.target_revenue:
                    concert_target += float(c.target_revenue)
                if c.break_even_point:
                    concert_bep += float(c.break_even_point)
            dr = all_daily.aggregate(mn=Min('date'), mx=Max('date'))
            if dr.get('mn') and dr.get('mx'):
                concert_date_min = dr['mn']
                concert_date_max = dr['mx']
        concert_count = concerts.count()

        # 뮤지컬 (공연명별 대표 1건, 최신 업로드, 입금만)
        musicals = Performance.objects.filter(genre='musical').order_by('id')
        seen_titles = set()
        representative_musicals = [p for p in musicals if p.title not in seen_titles and not seen_titles.add(p.title)]
        musical_revenue = 0
        musical_tickets = 0
        musical_target = 0
        musical_bep = 0
        for perf in representative_musicals:
            if perf.target_revenue:
                musical_target += float(perf.target_revenue)
            if perf.break_even_point:
                musical_bep += float(perf.break_even_point)
            latest_log = (
                PerformanceSalesUploadLog.objects
                .filter(performance=perf)
                .order_by('-uploaded_at', '-id')
                .first()
            )
            if latest_log:
                qs = MusicalEpisodeSales.objects.filter(performance=perf, upload_log=latest_log)
                rev = qs.aggregate(total=Sum('paid_revenue'))
                tkt = qs.aggregate(total=Sum('paid_ticket_count'))
                musical_revenue += float(rev['total'] or 0)
                musical_tickets += int(tkt['total'] or 0)
                dr = qs.aggregate(mn=Min('show_date'), mx=Max('show_date'))
                if dr.get('mn') and dr.get('mx'):
                    musical_date_min = min(musical_date_min, dr['mn']) if musical_date_min else dr['mn']
                    musical_date_max = max(musical_date_max, dr['mx']) if musical_date_max else dr['mx']
        musical_today_rev = MusicalEpisodeSales.objects.filter(
            performance__genre='musical',
            show_date=today,
        ).aggregate(total=Sum('paid_revenue'))
        musical_today_tkt = MusicalEpisodeSales.objects.filter(
            performance__genre='musical',
            show_date=today,
        ).aggregate(total=Sum('paid_ticket_count'))
        musical_today_revenue = float(musical_today_rev['total'] or 0)
        musical_today_tickets = int(musical_today_tkt['total'] or 0)
        musical_count = len(representative_musicals)

        # 연극 (구현 전, 0)
        theater_count = Performance.objects.filter(genre='theater').count()
        theater_revenue = 0
        theater_tickets = 0
        theater_today_revenue = 0
        theater_today_tickets = 0

        total_revenue = concert_revenue + musical_revenue + theater_revenue
        total_ticket_count = concert_tickets + musical_tickets + theater_tickets
        today_revenue = concert_today_revenue + musical_today_revenue + theater_today_revenue
        today_ticket_count = concert_today_tickets + musical_today_tickets + theater_today_tickets
        total_target_revenue = concert_target + musical_target
        total_break_even_point = concert_bep + musical_bep
        data_start_date = None
        data_end_date = None
        if concert_date_min is not None:
            data_start_date = concert_date_min if data_start_date is None else min(data_start_date, concert_date_min)
            data_end_date = concert_date_max if data_end_date is None else max(data_end_date, concert_date_max)
        if musical_date_min is not None:
            data_start_date = musical_date_min if data_start_date is None else min(data_start_date, musical_date_min)
            data_end_date = musical_date_max if data_end_date is None else max(data_end_date, musical_date_max)

        return JsonResponse({
            'success': True,
            'data': {
                'total_revenue': total_revenue,
                'total_ticket_count': total_ticket_count,
                'today_revenue': today_revenue,
                'today_ticket_count': today_ticket_count,
                'total_target_revenue': total_target_revenue,
                'total_break_even_point': total_break_even_point,
                'data_start_date': data_start_date.isoformat() if data_start_date else None,
                'data_end_date': data_end_date.isoformat() if data_end_date else None,
                'genres': {
                    'concert': {
                        'total_revenue': concert_revenue,
                        'total_ticket_count': concert_tickets,
                        'today_revenue': concert_today_revenue,
                        'today_ticket_count': concert_today_tickets,
                        'performance_count': concert_count,
                        'target_revenue': concert_target,
                        'break_even_point': concert_bep,
                    },
                    'musical': {
                        'total_revenue': musical_revenue,
                        'total_ticket_count': musical_tickets,
                        'today_revenue': musical_today_revenue,
                        'today_ticket_count': musical_today_tickets,
                        'performance_count': musical_count,
                        'target_revenue': musical_target,
                        'break_even_point': musical_bep,
                    },
                    'theater': {
                        'total_revenue': theater_revenue,
                        'total_ticket_count': theater_tickets,
                        'today_revenue': theater_today_revenue,
                        'today_ticket_count': theater_today_tickets,
                        'performance_count': theater_count,
                        'target_revenue': 0,
                        'break_even_point': 0,
                    },
                },
            },
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_overall_period_revenue_data(request):
    """전체 대시보드 기간별 매출 API (콘서트+뮤지컬 합계, 일/주/월)"""
    try:
        period_type = request.GET.get('period_type', 'daily')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        today = datetime.now().date()
        if not start_date_str or not end_date_str:
            if period_type == 'daily':
                end_date = today
                start_date = end_date - timedelta(days=29)
            elif period_type == 'weekly':
                end_date = today
                start_date = end_date - timedelta(weeks=3, days=end_date.weekday())
            else:
                end_date = today
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

        ignore_booking_sites = ['미', '미지정', '합계', 'TOTAL', '계', '전체', '총계', '유료 계', '초대']

        # 콘서트 기간별 합계
        concert_by_period = defaultdict(float)
        daily_sales = PerformanceDailySales.objects.filter(
            performance__genre='concert',
            date__gte=start_date,
            date__lte=end_date,
        ).exclude(booking_site__name__in=ignore_booking_sites)
        for sale in daily_sales:
            d = sale.date
            rev = float(sale.paid_revenue or 0) + float(sale.unpaid_revenue or 0)
            if period_type == 'daily':
                key = d.strftime('%Y-%m-%d')
            elif period_type == 'weekly':
                key = (d - timedelta(days=d.weekday())).strftime('%Y-%m-%d')
            else:
                key = d.strftime('%Y-%m')
            concert_by_period[key] += rev

        # 뮤지컬 기간별 합계 (최신 업로드, 입금만)
        musical_by_period = defaultdict(float)
        musicals = Performance.objects.filter(genre='musical').order_by('id')
        seen_titles = set()
        representative_musicals = [p for p in musicals if p.title not in seen_titles and not seen_titles.add(p.title)]
        latest_log_subq = (
            PerformanceSalesUploadLog.objects
            .filter(performance=OuterRef('performance'))
            .order_by('-uploaded_at', '-id')
        )
        episodes = MusicalEpisodeSales.objects.filter(
            performance__genre='musical',
            show_date__gte=start_date,
            show_date__lte=end_date,
            upload_log=Subquery(latest_log_subq.values('id')[:1]),
        )
        for ep in episodes:
            d = ep.show_date
            rev = float(ep.paid_revenue or 0)
            if period_type == 'daily':
                key = d.strftime('%Y-%m-%d')
            elif period_type == 'weekly':
                key = (d - timedelta(days=d.weekday())).strftime('%Y-%m-%d')
            else:
                key = d.strftime('%Y-%m')
            musical_by_period[key] += rev

        all_periods = sorted(set(concert_by_period.keys()) | set(musical_by_period.keys()))

        return JsonResponse({
            'success': True,
            'data': {
                'periods': all_periods,
                'concert': {k: concert_by_period.get(k, 0) for k in all_periods},
                'musical': {k: musical_by_period.get(k, 0) for k in all_periods},
            },
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


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
            break_even_point = float(concert.break_even_point) if concert.break_even_point is not None else None
            
            # 달성율 계산
            achievement_rate = 0
            if target_revenue > 0:
                achievement_rate = (concert_revenue / target_revenue) * 100
            
            concert_list.append({
                'id': concert.id,
                'title': concert.title,
                'target_revenue': target_revenue,
                'break_even_point': break_even_point,
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
def get_musical_aggregated_summary_data(request):
    """뮤지컬 통합 대시보드 요약 데이터 API (공연별 최신 업로드 회차 기준).
    총 매출·판매 매수는 상세 대시보드와 동일하게 입금(paid)만 사용하여,
    각 뮤지컬 상세 페이지의 합계를 더하면 장르별 총계와 일치한다."""
    try:
        musicals = Performance.objects.filter(genre='musical').order_by('id')

        if not musicals.exists():
            return JsonResponse({
                'success': True,
                'data': {
                    'total_revenue': 0,
                    'total_ticket_count': 0,
                    'today_revenue': 0,
                    'today_ticket_count': 0,
                    'total_target_revenue': 0,
                    'total_break_even_point': 0,
                    'total_seats': 0,
                    'musical_list': [],
                    'data_start_date': None,
                    'data_end_date': None,
                }
            })

        # 공연명(title)별 대표 1건만 사용 (동일 공연이 중복 등록된 경우 2배 집계 방지)
        seen_titles = set()
        representative_musicals = [p for p in musicals if p.title not in seen_titles and not seen_titles.add(p.title)]

        today = datetime.now().date()

        total_revenue = 0
        total_ticket_count = 0
        total_target_revenue = 0
        total_break_even_point = 0
        total_seats = 0
        musical_list = []
        data_start_date = None  # 매출 데이터 실제 기간 (기간별 그래프/테이블 기본값용)
        data_end_date = None

        for perf in representative_musicals:
            latest_log = (
                PerformanceSalesUploadLog.objects
                .filter(performance=perf)
                .order_by('-uploaded_at', '-id')
                .first()
            )
            if latest_log:
                episode_qs = MusicalEpisodeSales.objects.filter(performance=perf, upload_log=latest_log)
                # 상세 대시보드와 동일: 입금(paid)만 사용 → 상세 각 공연 합계 = 장르별 총계
                rev = episode_qs.aggregate(total=Sum('paid_revenue'))
                tkt = episode_qs.aggregate(total=Sum('paid_ticket_count'))
                perf_revenue = float(rev['total'] or 0)
                perf_tickets = int(tkt['total'] or 0)
                dr = episode_qs.aggregate(mn=Min('show_date'), mx=Max('show_date'))
                if dr.get('mn') and dr.get('mx'):
                    data_start_date = min(data_start_date, dr['mn']) if data_start_date else dr['mn']
                    data_end_date = max(data_end_date, dr['mx']) if data_end_date else dr['mx']
            else:
                perf_revenue = 0
                perf_tickets = 0

            total_revenue += perf_revenue
            total_ticket_count += perf_tickets

            if perf.target_revenue:
                total_target_revenue += float(perf.target_revenue)
            if perf.break_even_point:
                total_break_even_point += float(perf.break_even_point)
            for sg in perf.seat_grades.all():
                total_seats += sg.seat_count

            target_revenue = float(perf.target_revenue) if perf.target_revenue else 0
            achievement_rate = (perf_revenue / target_revenue * 100) if target_revenue > 0 else 0
            break_even_point = float(perf.break_even_point) if perf.break_even_point is not None else None
            musical_list.append({
                'id': perf.id,
                'title': perf.title,
                'target_revenue': target_revenue,
                'break_even_point': break_even_point,
                'total_revenue': perf_revenue,
                'achievement_rate': achievement_rate,
            })

        today_episodes = MusicalEpisodeSales.objects.filter(
            performance__genre='musical',
            show_date=today,
        )
        # 상세 대시보드와 동일: 입금(paid)만 사용
        today_rev = today_episodes.aggregate(total=Sum('paid_revenue'))
        today_revenue = float(today_rev['total'] or 0)
        today_ticket_result = today_episodes.aggregate(total=Sum('paid_ticket_count'))
        today_ticket_count = int(today_ticket_result['total'] or 0)

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
                'musical_list': musical_list,
                'data_start_date': data_start_date.isoformat() if data_start_date else None,
                'data_end_date': data_end_date.isoformat() if data_end_date else None,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_musical_period_revenue_data(request):
    """뮤지컬 통합 대시보드 기간별 매출 데이터 API (show_date 기준).
    공연별 최신 업로드 회차만 사용·입금(paid)만 집계·공연명별 대표 1건으로 요약·상세와 일치."""
    try:
        period_type = request.GET.get('period_type', 'daily')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        today = datetime.now().date()
        if not start_date_str or not end_date_str:
            if period_type == 'daily':
                end_date = today
                start_date = end_date - timedelta(days=29)
            elif period_type == 'weekly':
                end_date = today
                start_date = end_date - timedelta(weeks=3, days=end_date.weekday())
            else:
                end_date = today
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

        musicals = Performance.objects.filter(genre='musical').order_by('id')
        # 공연명별 대표 1건 (요약 대시보드·상세와 동일)
        seen_titles = set()
        representative_musicals = [p for p in musicals if p.title not in seen_titles and not seen_titles.add(p.title)]
        title_to_rep_id = {p.title: p.id for p in representative_musicals}

        # 공연별 최신 업로드 로그만 사용 (요약·상세와 동일)
        latest_log_subq = (
            PerformanceSalesUploadLog.objects
            .filter(performance=OuterRef('performance'))
            .order_by('-uploaded_at', '-id')
        )
        episodes = (
            MusicalEpisodeSales.objects.filter(
                performance__genre='musical',
                show_date__gte=start_date,
                show_date__lte=end_date,
                upload_log=Subquery(latest_log_subq.values('id')[:1]),
            )
            .select_related('performance')
        )

        # 입금(paid)만 사용 (상세·요약과 동일)
        period_data = defaultdict(lambda: defaultdict(float))
        for ep in episodes:
            show_date = ep.show_date
            rep_id = title_to_rep_id.get(ep.performance.title, ep.performance.id)
            revenue = float(ep.paid_revenue or 0)
            if period_type == 'daily':
                period_key = show_date.strftime('%Y-%m-%d')
            elif period_type == 'weekly':
                week_start = show_date - timedelta(days=show_date.weekday())
                period_key = week_start.strftime('%Y-%m-%d')
            else:
                period_key = show_date.strftime('%Y-%m')
            period_data[period_key][rep_id] += revenue

        periods = sorted(period_data.keys())
        performances = [{'id': p.id, 'title': p.title} for p in representative_musicals]
        data = {k: dict(v) for k, v in period_data.items()}

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
    today = datetime.now().date()

    if not start_date_str or not end_date_str:
        if performance.performance_end and performance.performance_end < today:
            end_date = performance.performance_end
        else:
            end_date = today
        start_date = end_date - timedelta(days=13)

        has_sales_in_range = PerformanceDailySales.objects.filter(
            performance=performance,
            date__gte=start_date,
            date__lte=end_date
        ).exclude(
            booking_site__name__in=ignore_booking_sites
        ).exists()

        if not has_sales_in_range:
            latest_sale_date = PerformanceDailySales.objects.filter(
                performance=performance
            ).exclude(
                booking_site__name__in=ignore_booking_sites
            ).aggregate(max_date=Max('date'))['max_date']
            if latest_sale_date:
                end_date = latest_sale_date
                start_date = end_date - timedelta(days=13)
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

    # 예매처별 비중용 전체 기간 집계 (필터 기간과 무관)
    booking_site_summary_all_time = []
    all_time_site_rows = (
        PerformanceDailySales.objects
        .filter(
            performance=performance,
            booking_site__isnull=False,
        )
        .exclude(
            booking_site__name__in=ignore_booking_sites
        )
        .values('booking_site__name')
        .annotate(
            revenue=Sum('paid_revenue'),
            tickets=Sum('paid_ticket_count')
        )
        .order_by('booking_site__name')
    )
    for row in all_time_site_rows:
        booking_site_summary_all_time.append({
            'site': row['booking_site__name'],
            'revenue': float(row['revenue'] or 0),
            'tickets': int(row['tickets'] or 0),
        })
    
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
    
    def get_upload_file_date(filename):
        match = re.search(r'(\d{4})(?=\.[^.]+$)', filename or '')
        if not match:
            return None
        month = int(match.group(1)[:2])
        day = int(match.group(1)[2:])
        base_year = performance.performance_start.year if performance.performance_start else datetime.now().year
        if performance.performance_start and month < performance.performance_start.month:
            base_year += 1
        try:
            return datetime(base_year, month, day).date()
        except ValueError:
            return None

    latest_file_date = None
    upload_logs = PerformanceSalesUploadLog.objects.filter(
        performance=performance
    ).values_list('original_filename', flat=True)
    for filename in upload_logs:
        file_date = get_upload_file_date(filename)
        if not file_date:
            continue
        if latest_file_date is None or file_date > latest_file_date:
            latest_file_date = file_date

    # 총 매출 계산 (일일 판매 유료 계 누적)
    paid_summary_qs = PerformanceDailySales.objects.filter(
        performance=performance,
        booking_site__name='유료 계'
    )
    total_end_date = latest_file_date or today
    paid_summary_qs = paid_summary_qs.filter(date__lte=total_end_date)
    has_paid_summary = paid_summary_qs.exists()

    paid_total = paid_summary_qs.aggregate(total=Sum('paid_revenue'))['total'] or 0
    total_revenue = float(paid_total)

    total_ticket_count = paid_summary_qs.aggregate(total=Sum('paid_ticket_count'))['total'] or 0

    if not has_paid_summary:
        paid_total = sales_data.aggregate(total=Sum('paid_revenue'))['total'] or 0
        unpaid_total = sales_data.aggregate(total=Sum('unpaid_revenue'))['total'] or 0
        total_revenue = float(paid_total) + float(unpaid_total)

        total_ticket_paid = sales_data.aggregate(total=Sum('paid_ticket_count'))['total'] or 0
        total_ticket_unpaid = sales_data.aggregate(total=Sum('unpaid_ticket_count'))['total'] or 0
        total_ticket_count = total_ticket_paid + total_ticket_unpaid
    
    # 등급별 판매현황 데이터 (PerformanceDailySalesGrade에서 합산)
    def build_grade_sales_data(range_start, range_end):
        grade_sales = {}
        grade_sales_qs = PerformanceDailySalesGrade.objects.filter(
            daily_sales__performance=performance,
            daily_sales__date__gte=range_start,
            daily_sales__date__lte=range_end
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

            grade_sales[grade_name] = {
                'paid_count': paid_count,
                'unpaid_count': unpaid_count,
                'free_count': free_count,
                'paid_occupancy_rate': paid_occupancy_rate,
                'total_occupancy_rate': total_occupancy_rate,
                'total_count': total_count,
            }
        return grade_sales

    if latest_file_date:
        grade_sales_data = build_grade_sales_data(latest_file_date, latest_file_date)
    else:
        grade_sales_data = build_grade_sales_data(start_date, end_date)

    if not grade_sales_data:
        latest_grade_date = PerformanceDailySalesGrade.objects.filter(
            daily_sales__performance=performance
        ).aggregate(max_date=Max('daily_sales__date'))['max_date']
        if latest_grade_date:
            grade_sales_data = build_grade_sales_data(latest_grade_date, latest_grade_date)
    
    # 나머지 섹션은 빈 데이터로 반환 (추후 확장)
    final_sales = PerformanceFinalSales.objects.filter(
        performance=performance,
        booking_site__isnull=True
    ).order_by('-updated_at').first()
    discount_sales_data = final_sales.booking_site_discount_sales if final_sales else {}
    age_gender_sales_data = final_sales.age_gender_sales if final_sales else []
    payment_method_sales_data = final_sales.payment_method_sales if final_sales else {}
    card_sales_data = {}
    if final_sales:
        card_sales_data = {
            item.get('card_type'): {
                'count': item.get('count', 0),
                'amount': item.get('amount', 0)
            }
            for item in (final_sales.card_sales_summary or [])
            if item.get('card_type')
        }
    sales_channel_sales_data = final_sales.sales_channel_sales if final_sales else []
    region_sales_groups_data = final_sales.region_sales if final_sales else []
    if final_sales and final_sales.seoul_region_sales:
        region_sales_groups_data = [
            {'title': '지역별', 'rows': final_sales.region_sales or []},
            {'title': '서울 지역별', 'rows': final_sales.seoul_region_sales or []},
            {'title': '경기 지역별', 'rows': final_sales.gyeonggi_region_sales or []},
        ]
    final_report_visibility = {
        'has_discount_sales': bool(discount_sales_data),
        'has_age_gender_sales': bool(age_gender_sales_data),
        'has_payment_method_sales': bool(payment_method_sales_data),
        'has_card_sales': bool(card_sales_data),
        'has_sales_channel_sales': bool(sales_channel_sales_data),
        'has_region_sales': bool(region_sales_groups_data),
    }
    
    return JsonResponse({
        'success': True,
        'data': {
            'dates': date_list,
            'applied_start_date': start_date.strftime('%Y-%m-%d'),
            'applied_end_date': end_date.strftime('%Y-%m-%d'),
            'booking_sites': booking_sites,
            'daily_revenue': daily_revenue_data,
            'daily_tickets': daily_ticket_data,
            'booking_site_summary_all_time': booking_site_summary_all_time,
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
            'region_sales_groups': region_sales_groups_data,
            'final_report_visibility': final_report_visibility,
        }
    })


@login_required
@require_http_methods(["GET"])
def get_musical_dashboard_data(request, pk):
    """뮤지컬 공연별 대시보드 데이터 API"""
    performance = get_object_or_404(Performance, id=pk, genre='musical')

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    today = datetime.now().date()
    if not start_date_str or not end_date_str:
        if performance.performance_end and performance.performance_end < today:
            end_date = performance.performance_end
        else:
            end_date = today
        start_date = end_date - timedelta(days=13)
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': '올바른 날짜 형식이 아니에요'}, status=400)

    latest_upload_log = (
        PerformanceSalesUploadLog.objects
        .filter(performance=performance)
        .order_by('-uploaded_at', '-id')
        .first()
    )

    if latest_upload_log:
        episode_qs = MusicalEpisodeSales.objects.filter(
            performance=performance,
            upload_log=latest_upload_log
        )
    else:
        episode_qs = MusicalEpisodeSales.objects.none()
    total_revenue = float(episode_qs.aggregate(total=Sum('paid_revenue'))['total'] or 0)
    total_ticket_count = int(episode_qs.aggregate(total=Sum('paid_ticket_count'))['total'] or 0)

    target_revenue = float(performance.target_revenue) if performance.target_revenue else None
    break_even_point = float(performance.break_even_point) if performance.break_even_point else None

    total_seats = 0
    for seat_grade in performance.seat_grades.all():
        total_seats += seat_grade.seat_count

    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    range_qs = episode_qs.filter(show_date__gte=start_date, show_date__lte=end_date)
    daily_agg = range_qs.values('show_date').annotate(
        revenue=Sum('paid_revenue'),
        tickets=Sum('paid_ticket_count'),
    ).order_by('show_date')
    revenue_map = {item['show_date'].strftime('%Y-%m-%d'): float(item['revenue'] or 0) for item in daily_agg}
    ticket_map = {item['show_date'].strftime('%Y-%m-%d'): int(item['tickets'] or 0) for item in daily_agg}

    daily_revenue = {d: {'뮤지컬': {'paid': revenue_map.get(d, 0), 'unpaid': 0}} for d in date_list}
    daily_tickets = {d: {'뮤지컬': {'paid': ticket_map.get(d, 0), 'unpaid': 0}} for d in date_list}

    table_rows = []
    for episode in episode_qs.order_by('episode_no'):
        cast_items = [name for name in (episode.cast_map or {}).values() if name]
        table_rows.append({
            'episode_no': episode.episode_no,
            'show_date': episode.show_date.strftime('%Y-%m-%d') if episode.show_date else '',
            'show_day': episode.show_day or '',
            'show_time': episode.show_time.strftime('%H:%M') if episode.show_time else '',
            'cast': ', '.join(cast_items),
            'paid': {
                'count': int(episode.paid_ticket_count or 0),
                'rate': float(episode.paid_rate) if episode.paid_rate is not None else None,
                'revenue': float(episode.paid_revenue or 0),
            },
            'unpaid': {
                'count': int(episode.unpaid_ticket_count or 0),
                'rate': float(episode.unpaid_rate) if episode.unpaid_rate is not None else None,
                'revenue': float(episode.unpaid_revenue or 0),
            },
            'invited': {
                'count': int(episode.invited_ticket_count or 0),
                'rate': float(episode.invited_rate) if episode.invited_rate is not None else None,
            },
            'total_paid': {
                'count': int(episode.total_paid_ticket_count or 0),
                'rate': float(episode.total_paid_rate) if episode.total_paid_rate is not None else None,
            },
            'remark': episode.remark or '',
        })

    return JsonResponse({
        'success': True,
        'data': {
            'dates': date_list,
            'applied_start_date': start_date.strftime('%Y-%m-%d'),
            'applied_end_date': end_date.strftime('%Y-%m-%d'),
            'booking_sites': ['뮤지컬'],
            'daily_revenue': daily_revenue,
            'daily_tickets': daily_tickets,
            'target_revenue': target_revenue,
            'break_even_point': break_even_point,
            'total_seats': total_seats,
            'total_revenue': total_revenue,
            'total_ticket_count': total_ticket_count,
            'episode_rows': table_rows,
        }
    })


@login_required
@require_http_methods(["GET", "POST"])
def marketing_memos(request, pk):
    """공연별 마케팅 메모 목록 조회 및 생성 API"""
    performance = get_object_or_404(Performance, pk=pk)

    if request.method == "GET":
        memos_qs = MarketingMemo.objects.filter(performance=performance).order_by('date', '-created_at').values(
            'id', 'date', 'content', 'created_at'
        )
        memo_by_date = defaultdict(list)
        for m in memos_qs:
            memo_by_date[m['date'].strftime('%Y-%m-%d')].append({
                'id': m['id'],
                'content': m['content'],
                'created_at': m['created_at'].strftime('%Y-%m-%d %H:%M'),
            })
        return JsonResponse({'success': True, 'data': {'memos': dict(memo_by_date)}})

    # POST: 메모 생성
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'}, status=400)

    date_str = body.get('date', '').strip()
    content = body.get('content', '').strip()
    if not date_str or not content:
        return JsonResponse({'success': False, 'error': '날짜와 내용을 입력해주세요.'}, status=400)

    try:
        memo = MarketingMemo.objects.create(
            performance=performance,
            date=date_str,
            content=content,
            created_by=request.user,
        )
    except Exception:
        return JsonResponse({'success': False, 'error': '메모 저장 중 오류가 발생했습니다.'}, status=500)

    return JsonResponse({
        'success': True,
        'data': {
            'id': memo.id,
            'date': str(memo.date),
            'content': memo.content,
            'created_at': memo.created_at.strftime('%Y-%m-%d %H:%M'),
        },
    })


@login_required
@require_http_methods(["PATCH", "DELETE"])
def marketing_memo_detail(request, pk, memo_id):
    """마케팅 메모 수정/삭제 API"""
    performance = get_object_or_404(Performance, pk=pk)
    memo = get_object_or_404(MarketingMemo, pk=memo_id, performance=performance)

    if request.method == "DELETE":
        memo.delete()
        return JsonResponse({'success': True})

    # PATCH: 메모 수정
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'}, status=400)

    content = body.get('content', '').strip()
    if not content:
        return JsonResponse({'success': False, 'error': '내용을 입력해주세요.'}, status=400)

    memo.content = content
    memo.save(update_fields=['content', 'updated_at'])

    return JsonResponse({
        'success': True,
        'data': {
            'id': memo.id,
            'date': str(memo.date),
            'content': memo.content,
            'created_at': memo.created_at.strftime('%Y-%m-%d %H:%M'),
        },
    })
