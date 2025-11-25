from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from decimal import Decimal
import json
from performance.models import Performance
from data_management.models import ConcertDailySales, ConcertFinalSales


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


@login_required
@require_http_methods(["GET"])
def get_concert_dashboard_data(request, pk):
    """콘서트 대시보드 데이터 API"""
    try:
        performance = get_object_or_404(Performance, id=pk, genre='concert')
    except:
        return JsonResponse({'success': False, 'error': '공연을 찾을 수 없어요'}, status=404)
    
    # 날짜 범위 파라미터
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # 기본값: 최근 7일
    if not start_date_str or not end_date_str:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': '올바른 날짜 형식이 아니에요'}, status=400)
    
    # 날짜 범위 내 모든 날짜 생성 (빈 데이터도 포함)
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    # 매출 데이터 조회
    sales_data = ConcertDailySales.objects.filter(
        performance=performance,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date', 'booking_site')
    
    # 예매처 목록 (실제 데이터에서 추출)
    booking_sites = list(sales_data.values_list('booking_site', flat=True).distinct())
    
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
        site = sale.booking_site
        
        if date_str not in daily_revenue_data:
            daily_revenue_data[date_str] = {}
            daily_ticket_data[date_str] = {}
        
        if site not in daily_revenue_data[date_str]:
            daily_revenue_data[date_str][site] = {'paid': 0, 'unpaid': 0}
            daily_ticket_data[date_str][site] = {'paid': 0, 'unpaid': 0}
        
        # Decimal을 float으로 변환
        daily_revenue_data[date_str][site]['paid'] = float(sale.paid_revenue) if sale.paid_revenue else 0
        daily_revenue_data[date_str][site]['unpaid'] = float(sale.unpaid_revenue) if sale.unpaid_revenue else 0
        daily_ticket_data[date_str][site]['paid'] = sale.paid_ticket_count or 0
        daily_ticket_data[date_str][site]['unpaid'] = sale.unpaid_ticket_count or 0
    
    # 총 좌석수 계산 (seat_counts JSON 필드에서 합산)
    total_seats = 0
    if performance.seat_counts:
        for grade, count in performance.seat_counts.items():
            if isinstance(count, (int, float)):
                total_seats += count
    
    # 목표액, 손익분기점
    target_revenue = float(performance.target_revenue) if performance.target_revenue else None
    break_even_point = float(performance.break_even_point) if performance.break_even_point else None
    
    # 총 매출 계산 (전체 기간)
    paid_total = sales_data.aggregate(total=Sum('paid_revenue'))['total'] or 0
    unpaid_total = sales_data.aggregate(total=Sum('unpaid_revenue'))['total'] or 0
    total_revenue = float(paid_total) + float(unpaid_total)
    
    # 등급별 판매현황 데이터 (ConcertFinalSales에서 가져오기)
    grade_sales_data = {}
    # 할인권종별 판매현황 데이터 (ConcertFinalSales에서 가져오기)
    discount_sales_data = {}
    # 성별, 연령대별 판매현황 데이터 (ConcertFinalSales에서 가져오기)
    age_gender_sales_data = []
    # 결제수단별 판매현황 데이터 (ConcertFinalSales에서 가져오기)
    payment_method_sales_data = {}
    # 카드별 매출집계 데이터 (ConcertFinalSales에서 가져오기)
    card_sales_data = {}
    # 판매경로별 판매현황 데이터 (ConcertFinalSales에서 가져오기)
    sales_channel_sales_data = {}
    # 지역별 판매현황 데이터 (ConcertFinalSales에서 가져오기)
    region_sales_data = {}
    final_sales = ConcertFinalSales.objects.filter(performance=performance)
    
    # 모든 예매처의 등급별 데이터를 합산
    for final_sale in final_sales:
        if final_sale.grade_sales_summary:
            for grade, grade_data in final_sale.grade_sales_summary.items():
                if grade not in grade_sales_data:
                    grade_sales_data[grade] = {
                        'paid_count': 0,
                        'free_count': 0,
                        'revenue': 0,
                        'paid_occupancy_rate': 0,
                        'total_occupancy_rate': 0,
                        'total_count': 0,
                    }
                
                # 데이터 합산
                grade_sales_data[grade]['paid_count'] += grade_data.get('paid_count', 0)
                grade_sales_data[grade]['free_count'] += grade_data.get('free_count', 0)
                grade_sales_data[grade]['revenue'] += float(grade_data.get('revenue', 0))
                grade_sales_data[grade]['total_count'] += grade_data.get('total_count', 0)
                
                # 점유율은 가중 평균으로 계산 (또는 마지막 값 사용)
                # 간단하게는 마지막 값 사용
                if grade_data.get('paid_occupancy_rate'):
                    grade_sales_data[grade]['paid_occupancy_rate'] = grade_data.get('paid_occupancy_rate', 0)
                if grade_data.get('total_occupancy_rate'):
                    grade_sales_data[grade]['total_occupancy_rate'] = grade_data.get('total_occupancy_rate', 0)
        
        # 할인권종별 판매현황 데이터
        if final_sale.booking_site_discount_sales:
            site = final_sale.booking_site
            if site not in discount_sales_data:
                discount_sales_data[site] = []
            
            # 할인권종별 데이터 추가
            if isinstance(final_sale.booking_site_discount_sales, dict):
                for discount_type, discount_data in final_sale.booking_site_discount_sales.items():
                    if isinstance(discount_data, list):
                        discount_sales_data[site].extend(discount_data)
                    elif isinstance(discount_data, dict):
                        discount_sales_data[site].append(discount_data)
        
        # 성별, 연령대별 판매현황 데이터
        if final_sale.age_gender_sales:
            if isinstance(final_sale.age_gender_sales, list):
                # 모든 예매처의 데이터를 합산
                for age_gender_item in final_sale.age_gender_sales:
                    age_group = age_gender_item.get('age_group')
                    if age_group:
                        # 기존에 같은 연령대가 있는지 확인
                        existing_item = next((item for item in age_gender_sales_data if item.get('age_group') == age_group), None)
                        if existing_item:
                            # 기존 항목에 합산
                            existing_item['male_count'] = existing_item.get('male_count', 0) + age_gender_item.get('male_count', 0)
                            existing_item['female_count'] = existing_item.get('female_count', 0) + age_gender_item.get('female_count', 0)
                            existing_item['unknown_count'] = existing_item.get('unknown_count', 0) + age_gender_item.get('unknown_count', 0)
                            existing_item['total_count'] = existing_item.get('total_count', 0) + age_gender_item.get('total_count', 0)
                        else:
                            # 새 항목 추가
                            age_gender_sales_data.append({
                                'age_group': age_group,
                                'male_count': age_gender_item.get('male_count', 0),
                                'female_count': age_gender_item.get('female_count', 0),
                                'unknown_count': age_gender_item.get('unknown_count', 0),
                                'total_count': age_gender_item.get('total_count', 0),
                            })
        
        # 결제수단별 판매현황 데이터
        if final_sale.payment_method_sales:
            if isinstance(final_sale.payment_method_sales, list):
                for payment_item in final_sale.payment_method_sales:
                    payment_method = payment_item.get('payment_method', '')
                    if payment_method:
                        if payment_method not in payment_method_sales_data:
                            payment_method_sales_data[payment_method] = {
                                'count': 0,
                                'amount': 0,
                            }
                        payment_method_sales_data[payment_method]['count'] += payment_item.get('count', 0)
                        payment_method_sales_data[payment_method]['amount'] += float(payment_item.get('amount', 0))
        
        # 카드별 매출집계 데이터
        if final_sale.card_sales_summary:
            if isinstance(final_sale.card_sales_summary, list):
                for card_item in final_sale.card_sales_summary:
                    card_type = card_item.get('card_type', '')
                    if card_type:
                        if card_type not in card_sales_data:
                            card_sales_data[card_type] = {
                                'count': 0,
                                'amount': 0,
                            }
                        card_sales_data[card_type]['count'] += card_item.get('count', 0)
                        card_sales_data[card_type]['amount'] += float(card_item.get('amount', 0))
        
        # 판매경로별 판매현황 데이터
        if final_sale.sales_channel_sales:
            if isinstance(final_sale.sales_channel_sales, list):
                for channel_item in final_sale.sales_channel_sales:
                    sales_channel = channel_item.get('sales_channel', '')
                    if sales_channel:
                        if sales_channel not in sales_channel_sales_data:
                            sales_channel_sales_data[sales_channel] = {
                                'count': 0,
                                'amount': 0,
                            }
                        sales_channel_sales_data[sales_channel]['count'] += channel_item.get('count', 0)
                        sales_channel_sales_data[sales_channel]['amount'] += float(channel_item.get('amount', 0))
        
        # 지역별 판매현황 데이터
        if final_sale.region_sales:
            if isinstance(final_sale.region_sales, list):
                for region_item in final_sale.region_sales:
                    region = region_item.get('region', '')
                    if region:
                        if region not in region_sales_data:
                            region_sales_data[region] = {
                                'count': 0,
                            }
                        region_sales_data[region]['count'] += region_item.get('count', 0)
    
    # 연령대별로 정렬 (나이 순서대로)
    def sort_age_group(item):
        age_group = item.get('age_group', '')
        # 숫자 추출하여 정렬
        numbers = [int(x) for x in age_group.split() if x.isdigit()]
        return numbers[0] if numbers else 999
    
    age_gender_sales_data.sort(key=sort_age_group)
    
    return JsonResponse({
        'success': True,
        'data': {
            'dates': date_list,
            'booking_sites': booking_sites,
            'daily_revenue': daily_revenue_data,
            'daily_tickets': daily_ticket_data,
            'target_revenue': target_revenue,
            'break_even_point': break_even_point,
            'total_seats': total_seats,
            'total_revenue': total_revenue,
            'grade_sales': grade_sales_data,
            'discount_sales': discount_sales_data,
            'age_gender_sales': age_gender_sales_data,
            'payment_method_sales': payment_method_sales_data,
            'card_sales': card_sales_data,
            'sales_channel_sales': sales_channel_sales_data,
            'region_sales': region_sales_data,
        }
    })
