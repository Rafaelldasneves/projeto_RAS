from django.urls import path, include
from . import views

urlpatterns = [
    path('servidor/register/', views.RegisterUserView.as_view(), name="register_servidor"),
    path('', include('django.contrib.auth.urls')),
    path('servidor/', views.ListServidor.as_view(), name="list_servidor"),
    path('servidor/<int:pk>/detail/', views.DetailServidor.as_view(), name="detail_servidor"),
    path('servidor/<int:pk>/update/', views.UpdateServidor.as_view(), name="update_servidor"),
    path('servidor/<int:pk>/delete/', views.DeleteServidor.as_view(), name="delete_servidor"),
]
