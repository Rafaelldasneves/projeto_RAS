from django.contrib import admin
from .models import Period, Service, RegistrationService


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    fields = ['date', 'time_start', 'time_end', 'vacancies']


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_start', 'date_end', 'description')
    search_fields = ('name', 'description')
    inlines = [ServiceInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('period', 'date', 'time_start', 'time_end', 'vacancies', 'remaining_vacancies')
    list_filter = ('period', 'date')


@admin.register(RegistrationService)
class RegistrationServiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'status', 'registration_date')
    list_filter = ('status', 'service__period')
    list_editable = ('status',)
