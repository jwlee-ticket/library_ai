from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'data_management'

urlpatterns = [
    # 루트 경로는 매출 관리로 리다이렉트
    path('', RedirectView.as_view(pattern_name='data_management:performance_list', permanent=False), name='index'),
    
    # 매출 관리 - 공연 목록 (모든 장르)
    path('sales/', views.PerformanceListView.as_view(), name='performance_list'),
    
    # 공연 매출 관리 (특정 공연의 매출)
    path('sales/<int:performance_id>/', views.PerformanceSalesDetailView.as_view(), name='performance_sales_detail'),
    path('sales/<int:performance_id>/create/', views.PerformanceSalesCreateView.as_view(), name='performance_sales_create'),
    path('sales/<int:performance_id>/save-daily/', views.save_daily_sales, name='save_daily_sales'),
    path('sales/<int:performance_id>/get-daily/', views.get_daily_sales, name='get_daily_sales'),
    path('sales/<int:pk>/edit/', views.PerformanceSalesUpdateView.as_view(), name='performance_sales_update'),
    path('sales/<int:pk>/delete/', views.PerformanceSalesDeleteView.as_view(), name='performance_sales_delete'),
]
