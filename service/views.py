from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from django import forms
from .forms import PeriodForm, ServiceInlineFormSet, ServiceForm
from .models import Period, Service, RegistrationService
from django.utils import timezone


@permission_required('service.add_period', login_url='login')
def PeriodCreate(request):
    if request.method == 'POST':
        form = PeriodForm(request.POST)
        formset = ServiceInlineFormSet(request.POST, instance=Period())
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    period = form.save()
                    formset.instance = period
                    formset.save()
                messages.success(request, "Período e RAS criados com sucesso!")
                return redirect('period_list')
            except Exception as e:
                messages.error(request, f"Ocorreu um erro ao salvar: {e}")
        else:
            messages.error(request, "Erro de validação. Verifique os dados inseridos.")

    else:
        form = PeriodForm()
        formset = ServiceInlineFormSet(instance=Period())
    context = {
        'form': form,
        'formset': formset,
        'title': 'Criar Novo Período de Plantões'
    }
    return render(request, 'period_create.html', context)


class ServiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Service
    template_name = 'service_form.html'
    fields = ['date', 'time_start', 'time_end', 'vacancies']
    permission_required = 'service.add_service'

    def form_valid(self, form):
        period_pk = self.kwargs.get('period_pk')
        period = get_object_or_404(Period, pk=period_pk)
        form.instance.period = period
        if form.instance.date < period.date_start or form.instance.date > period.date_end:
            form.add_error('date', "A data do plantão deve estar dentro do período definido.")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Adiciona o Periodo pai ao contexto do template."""
        context = super().get_context_data(**kwargs)
        period_pk = self.kwargs.get('period_pk')
        period_pai = get_object_or_404(Period, pk=period_pk)
        context['period'] = period_pai
        return context

    def get_success_url(self):
        return reverse_lazy('period_detail', kwargs={'pk': self.kwargs['period_pk']})


class PeriodListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Period
    template_name = 'period_list.html'
    context_object_name = 'periods'
    paginate_by = 10
    permission_required = 'service.view_period'


class PeriodDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Period
    template_name = 'period_detail.html'
    paginate_by = 10
    context_object_name = 'period'
    permission_required = 'service.view_period'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = self.object.plantoes.all()
        return context


class PeriodUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Period
    form_class = PeriodForm
    template_name = 'period_update.html'
    success_url = reverse_lazy('period_list')
    success_message = "O Período e seus RAS foram atualizados com sucesso!"
    permission_required = 'service.change_period'
    widgets = {
        'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        'time_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        'time_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        'vacancies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
    }

    ServiceFormSet = inlineformset_factory(
        Period,
        Service,
        form=ServiceForm,
        fields=('date', 'time_start', 'time_end', 'vacancies'),
        extra=1,
        can_delete=True
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = self.ServiceFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['formset'] = self.ServiceFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class PeriodDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Period
    success_url = reverse_lazy('period_list')
    template_name = 'period_delete.html'
    permission_required = 'service.delete_period'

    def get_success_url(self):
        from django.contrib import messages
        messages.success(self.request, "O Período e todos os RAS associados foram excluídos permanentemente.")
        return reverse_lazy('period_list')


class ServiceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Service
    paginate_by = 10
    template_name = 'agents/Service_available_list.html'
    permission_required = 'service.view_service'

    def get_queryset(self):
        return Service.objects.filter(date__gte=timezone.now().date()).order_by('period__date_start', 'date', 'time_start')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services_future = self.get_queryset()

    # Agrupa os serviços por período
        service_por_period = {}
        for service in services_future:
            period = service.period
            service_por_period.setdefault(period, []).append(service)
        context['service_por_period'] = service_por_period

        # Todas as inscrições do usuário
        registrations_user = RegistrationService.objects.filter(user=self.request.user)

        # Serviços onde o usuário está inscrito (confirmado ou reserva)
        service_ids_registered = registrations_user.filter(
            status__in=['CONFIRMADO', 'RESERVA']
        ).values_list('service__id', flat=True)

        # Serviços onde o usuário cancelou
        service_ids_cancelled = registrations_user.filter(
            status='CANCELADO'
        ).values_list('service__id', flat=True)

        # Envia os conjuntos ao template
        context['service_ids_registered'] = set(service_ids_registered)
        context['service_ids_cancelled'] = set(service_ids_cancelled)

        return context


class ServiceRegistrationsView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Service
    template_name = 'service_registration.html'
    paginate_by = 10
    context_object_name = 'service'
    permission_required = 'service.add_service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirmados'] = self.object.registrations.filter(status='CONFIRMADO')
        context['reservas'] = self.object.registrations.filter(status='RESERVA')
        context['cancelados'] = self.object.registrations.filter(status='CANCELADO')
        return context


@login_required(login_url='login')
def apply_plantation(request, pk):
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        # 1. Verifica se o usuário já está inscrito neste plantão
        if RegistrationService.objects.filter(service=service, user=request.user).exists():
            messages.warning(request, "Você já está inscrito neste RAS.")
            return redirect('service_list')

        # 2. Implementação da Dinâmica: Vaga ou Reserva
        remaining_vacancies = service.remaining_vacancies

        if remaining_vacancies > 0:
            status_vacancie = 'CONFIRMADO'
            mensagem = f"Parabéns! Você foi CONFIRMADO no plantão do DIA {service.date.strftime('%d/%m/%y')} de {service.time_start.strftime('%H:%M')} as {service.time_end.strftime('%H:%M')}."
        else:
            status_vacancie = 'RESERVA'
            mensagem = f"As vagas estão esgotadas. Você entrou na lista de RESERVA para o plantão do DIA {service.date.strftime('%d/%m/%y')} de {service.time_start.strftime('%H:%M')} as {service.time_end.strftime('%H:%M')}."

        try:
            # 3. Cria a inscrição no banco de dados
            RegistrationService.objects.create(
                service=service,
                user=request.user,
                status=status_vacancie
            )
            messages.success(request, mensagem)
        except IntegrityError:
            # Caso raro de race condition ou falha na checagem inicial
            messages.error(request, "Ocorreu um erro. Tente novamente.")

        return redirect('my_subscriptions')

    return render(request, {'service': service})


@login_required(login_url='login')
def cancel_registration_service(request, pk):
    service = get_object_or_404(Service, pk=pk)

    try:
        registration = RegistrationService.objects.get(service=service, user=request.user)
    except RegistrationService.DoesNotExist:
        messages.warning(request, "Você não está inscrito(a) neste plantão.")
        return redirect('agents/service_list')

    if request.method == 'POST':
        with transaction.atomic():
            # Guarda o status anterior
            previous_status = registration.status

            # Cancela a inscrição
            registration.status = 'CANCELADO'
            registration.save()

            # Se estava CONFIRMADO, promove o primeiro da fila de RESERVA
            if previous_status == 'CONFIRMADO':
                next_reservation = RegistrationService.objects.filter(
                    service=service,
                    status='RESERVA'
                ).order_by('registration_date').first()

                if next_reservation:
                    next_reservation.status = 'CONFIRMADO'
                    next_reservation.save()
                    # Opcional: enviar notificação aqui

            messages.success(request, (
                f"Sua inscrição para o RAS do dia {service.date.strftime('%d/%m/%y')} "
                f"das {service.time_start.strftime('%H:%M')} às {service.time_end.strftime('%H:%M')} "
                "foi cancelada com sucesso."
            ))
            return redirect('my_subscriptions')

    return render(request, 'agents/confirmation_cancellation.html', {'service': service})


class MySubscriptionsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = RegistrationService
    paginate_by = 10
    template_name = 'agents/my_subscriptions_list.html'
    context_object_name = 'registrations'
    permission_required = 'service.view_registrationservice'

    def get_queryset(self):
        return RegistrationService.objects.filter(user=self.request.user).order_by('service__date')
