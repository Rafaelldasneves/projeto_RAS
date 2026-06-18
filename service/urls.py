from django.urls import path
from . import views

urlpatterns = [
    path('period/<int:period_pk>/new_service', views.ServiceCreateView.as_view(), name='new_service'),
    path('period/<int:pk>/registratios', views.ServiceRegistrationsView.as_view(), name='registrations_list'),
    path('registration/<int:registration_pk>/cancel/', views.cancel_registration_by_manager, name='cancel_registration_manager'),
    path('agents/service_available', views.ServiceListView.as_view(), name='service_list'),
    path('agents/<int:pk>/apply', views.apply_plantation, name='apply_plantation'),
    path('agents/my_subscriptions', views.MySubscriptionsListView.as_view(), name='my_subscriptions'),
    path('agents/<int:pk>/cancel_registration', views.cancel_registration_service, name='cancel_registration'),
    path('exportar-pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('relatorio-pdf/', views.relatorio_pdf_view, name='relatorio_pdf'),
    path('assinaturas-pdf/', views.assinaturas_pdf, name='assinaturas_pdf'),
]
