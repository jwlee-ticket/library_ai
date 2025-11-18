from django.urls import path
from . import views

app_name = 'performance'

urlpatterns = [
    path('', views.PerformanceListView.as_view(), name='list'),
    path('create/', views.PerformanceCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PerformanceDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PerformanceUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.PerformanceDeleteView.as_view(), name='delete'),
]

