from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from collections import OrderedDict
from service.models import Period


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation_limit = 5  # limite de reservas exibidas por plantão

        # Carrega os períodos e os plantões relacionados
        periods = (
            Period.objects
            .prefetch_related('plantoes__registrations__user')
            .order_by('-date_start')
        )

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
