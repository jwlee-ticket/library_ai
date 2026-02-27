from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.main_view, name='index'),
    path('dashboard-performance/', views.PerformanceDashboardListView.as_view(), name='list'),
    path('dashboard-performance/<int:pk>/', views.PerformanceDashboardDetailView.as_view(), name='detail'),
    path('dashboard-performance/<int:pk>/data/', views.get_concert_dashboard_data, name='concert_dashboard_data'),
    path('dashboard-performance/<int:pk>/musical-data/', views.get_musical_dashboard_data, name='musical_dashboard_data'),
    path('overview/', views.OverviewDashboardView.as_view(), name='overview'),
    path('overview/summary/', views.get_overall_aggregated_summary_data, name='overall_aggregated_summary'),
    path('overview/period-revenue/', views.get_overall_period_revenue_data, name='overall_period_revenue'),
    path('concert-overview/', views.ConcertOverviewDashboardView.as_view(), name='concert_overview'),
    path('concert-overview/summary/', views.get_concert_aggregated_summary_data, name='concert_aggregated_summary'),
    path('concert-overview/period-revenue/', views.get_concert_period_revenue_data, name='concert_period_revenue'),
    path('musical-overview/', views.MusicalOverviewDashboardView.as_view(), name='musical_overview'),
    path('musical-overview/summary/', views.get_musical_aggregated_summary_data, name='musical_aggregated_summary'),
    path('musical-overview/period-revenue/', views.get_musical_period_revenue_data, name='musical_period_revenue'),
]

