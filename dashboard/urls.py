from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.main_view, name='index'),
    path('dashboard-performance/', views.PerformanceDashboardListView.as_view(), name='list'),
    path('dashboard-performance/<int:pk>/', views.PerformanceDashboardDetailView.as_view(), name='detail'),
    path('dashboard-performance/<int:pk>/data/', views.get_concert_dashboard_data, name='concert_dashboard_data'),
    path('concert-overview/', views.ConcertOverviewDashboardView.as_view(), name='concert_overview'),
    path('concert-overview/summary/', views.get_concert_aggregated_summary_data, name='concert_aggregated_summary'),
    path('concert-overview/period-revenue/', views.get_concert_period_revenue_data, name='concert_period_revenue'),
]

