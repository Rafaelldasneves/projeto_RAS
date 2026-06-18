from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from collections import OrderedDict
from service.models import Period


class HomeView(LoginRequiredMixin, ListView):
    model = Period
    paginate_by = 5
    template_name = 'home.html'
    context_object_name = 'periods'

    def get_queryset(self):
        now = timezone.now()
        return Period.objects.filter(
            plantoes__date__gte=now.date()
        ).filter(
            Q(available_from__lte=now) | Q(available_from__isnull=True)
        ).filter(
            Q(available_until__gte=now) | Q(available_until__isnull=True)
        ).prefetch_related('plantoes__registrations__user').order_by('-date_start').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periods = context.get('page_obj').object_list if context.get('page_obj') else context.get('object_list', self.get_queryset())
        reservation_limit = 5

        grouped = OrderedDict()

        for period in periods:
            services = period.plantoes.all().order_by('date', 'time_start')

            for service in services:
                regs = service.registrations.all()
                service.confirmados = regs.filter(status='CONFIRMADO')
                service.reservas = regs.filter(status='RESERVA')[:reservation_limit]

            grouped[period] = services

        context['grouped_services'] = grouped
        context['reservation_limit'] = reservation_limit
        
        return context
