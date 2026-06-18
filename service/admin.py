from django.contrib import admin
from .models import Service, RegistrationService
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('period', 'date', 'time_start', 'time_end', 'vacancies', 'remaining_vacancies')
    list_filter = ('period', 'date')


@admin.register(RegistrationService)
class RegistrationServiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'status', 'registration_date')
    list_filter = ('status', 'service__period')
    list_editable = ('status',)
