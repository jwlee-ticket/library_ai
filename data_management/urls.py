from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'data_management'

urlpatterns = [
    # 루트 경로는 매출 관리로 리다이렉트
    path('', RedirectView.as_view(pattern_name='data_management:performance_list', permanent=False), name='index'),
    
    # 매출 관리 - 공연 목록 (모든 장르)
    path('sales/', views.PerformanceListView.as_view(), name='performance_list'),
    
    # 콘서트 매출 관리 (특정 공연의 매출)
    path('sales/concert/<int:performance_id>/', views.ConcertSalesListView.as_view(), name='concert_sales_detail'),
    path('sales/concert/<int:performance_id>/create/', views.ConcertSalesCreateView.as_view(), name='concert_sales_create'),
    path('sales/concert/<int:performance_id>/save-daily/', views.save_daily_sales, name='save_daily_sales'),
    path('sales/concert/<int:performance_id>/get-daily/', views.get_daily_sales, name='get_daily_sales'),
    path('sales/concert/<int:pk>/edit/', views.ConcertSalesUpdateView.as_view(), name='concert_sales_update'),
    path('sales/concert/<int:pk>/delete/', views.ConcertSalesDeleteView.as_view(), name='concert_sales_delete'),
    
    # 뮤지컬 매출 관리 (준비 중 - 나중에 구현)
    path('sales/musical/<int:performance_id>/', views.MusicalSalesListView.as_view(), name='musical_sales_list'),
    
    # 연극 매출 관리 (준비 중 - 나중에 구현)
    path('sales/theater/<int:performance_id>/', views.TheaterSalesListView.as_view(), name='theater_sales_list'),
]
