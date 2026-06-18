from django.urls import path
from . import views

urlpatterns = [
    path('', views.PeriodCreate, name="period_create"),
    path('periods/', views.PeriodListView.as_view(), name='period_list'),
    path('periods/<int:pk>/detail', views.PeriodDetailView.as_view(), name='period_detail'),
    path('period/<int:pk>/update', views.PeriodUpdateView.as_view(), name='period_update'),
    path('period/<int:pk>/delete', views.PeriodDeleteView.as_view(), name='period_delete'),
]