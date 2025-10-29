from django.urls import path
from . import views

urlpatterns = [
    path('', views.PeriodCreate, name="period_create"),
    path('periods/', views.PeriodListView.as_view(), name='period_list'),
    path('periods/<int:pk>/detail', views.PeriodDetailView.as_view(), name='period_detail'),
    path('period/<int:pk>/update', views.PeriodUpdateView.as_view(), name='period_update'),
    path('period/<int:pk>/delete', views.PeriodDeleteView.as_view(), name='period_delete'),
    path('period/<int:period_pk>/new_service', views.ServiceCreateView.as_view(), name='new_service'),
    path('period/<int:pk>/registratios', views.ServiceRegistrationsView.as_view(), name='registrations_list'),
    path('agents/service_available', views.ServiceListView.as_view(), name='service_list'),
    path('agents/<int:pk>/apply', views.apply_plantation, name='apply_plantation'),
    path('agents/my_subscriptions', views.MySubscriptionsListView.as_view(), name='my_subscriptions'),
    path('agents/<int:pk>/cancel_registration', views.cancel_registration_service, name='cancel_registration'),
]
