from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.main_view, name='index'),
    path('dashboard-performance/', views.PerformanceDashboardListView.as_view(), name='list'),
    path('dashboard-performance/<int:pk>/', views.PerformanceDashboardDetailView.as_view(), name='detail'),
    path('dashboard-performance/<int:pk>/data/', views.get_concert_dashboard_data, name='concert_dashboard_data'),
]

