from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', views.HomeView.as_view(), name='home'),
    path('period/', include('period.urls')),
    path('service/', include('service.urls')),
]
