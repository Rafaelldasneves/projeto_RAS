from django.urls import path, include
from . import views

urlpatterns = [
    path('servidor/register/', views.RegisterUserView.as_view(), name="register_servidor"),
    path('servidor/<int:pk>/reset-password/', views.reset_temporary_password, name='reset_temporary_password'),
    path('servidor/<int:pk>/detail/', views.DetailServidor.as_view(), name="detail_servidor"),
    path('servidor/<int:pk>/update/', views.UpdateServidor.as_view(), name="update_servidor"),
    path('servidor/<int:pk>/delete/', views.DeleteServidor.as_view(), name="delete_servidor"),
    path('servidor/change-password/', views.ForcePasswordChangeView.as_view(), name='force_password_change'),
    path('', include('django.contrib.auth.urls')),
    path('servidor/', views.ListServidor.as_view(), name="list_servidor"),
]
