from django.contrib import admin
from .models import Period
from service.models import Service


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    fields = ['date', 'time_start', 'time_end', 'vacancies']


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_start', 'date_end', 'available_from', 'available_until', 'description')
    search_fields = ('name', 'description')
    inlines = [ServiceInline]
