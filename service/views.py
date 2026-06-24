from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Prefetch, Q
from io import BytesIO
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.mail import EmailMessage
from weasyprint import HTML
from .models import Service, RegistrationService
from django.urls import reverse_lazy
from period.models import Period
from collections import OrderedDict
from datetime import datetime
import os
from django.conf import settings


def notify_reservation_promoted_to_confirmed(request, registration):
    user = registration.user
    service = registration.service
    # Envia e-mail de notificação    
    subject = "Sua reserva foi promovida para titular"
    message = (
        f"Olá {user.position.upper()}  {user.username.upper()},\n\n"
        "Uma vaga titular ficou disponível e sua inscrição no plantão foi promovida de RESERVA para TITULAR.\n\n"
        f"Plantão: {service.period.name} - {service.date.strftime('%d/%m/%Y')} "
        f"das {service.time_start.strftime('%H:%M:%S')} às {service.time_end.strftime('%H:%M:%S')}\n\n"
        "Acesse o sistema para ver os detalhes, Caso tenha dúvidas, entre em contato .\n\n"
        "Atenciosamente,\nSubcomandante da Guarda Civil Municipal"
    )

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
        bcc=['fabiianadesouza@gmail.com'],
    )

    # Enviando o e-mail
    email.send(fail_silently=False)
   
   
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


class ServiceListView(LoginRequiredMixin, ListView):
    model = Period
    paginate_by = 5
    template_name = 'agents/service_available_list.html'

    def get_queryset(self):
        now = timezone.now()
        return Period.objects.filter(
            plantoes__date__gte=now.date()
        ).filter(
            Q(available_from__lte=now) | Q(available_from__isnull=True)
        ).filter(
            Q(available_until__gte=now) | Q(available_until__isnull=True)
        ).order_by('date_start', 'date_end').prefetch_related(
            Prefetch('plantoes', queryset=Service.objects.filter(date__gte=now.date()).order_by('date', 'time_start'))
        ).distinct()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periods = context.get('page_obj').object_list if context.get('page_obj') else context.get('object_list', self.get_queryset())

        # Agrupa os serviços por período usando o prefetch
        service_por_period = {}
        for period in periods:
            period_services = {}
            # Usar os plantões já carregados pelo prefetch
            for service in period.plantoes.all():
                period_services.setdefault(service.date, []).append(service)
            
            service_por_period[period] = period_services

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
            mensagem = f"Parabéns! Você foi CONFIRMADO no plantão do DIA {service.date.strftime('%d/%m/%y')} de {service.time_start.strftime('%H:%M:%S')} as {service.time_end.strftime('%H:%M:%S')}."
           
        else:
            status_vacancie = 'RESERVA'
            mensagem = f"As vagas estão esgotadas. Você entrou na lista de RESERVA para o plantão do DIA {service.date.strftime('%d/%m/%y')} de {service.time_start.strftime('%H:%M:%S')} as {service.time_end.strftime('%H:%M:%S')}."

        try:
            # 3. Cria a inscrição no banco de dados
            RegistrationService.objects.create(
                service=service,
                user=request.user,
                status=status_vacancie
            )
            messages.success(request, mensagem)
        except IntegrityError:
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

                    notify_reservation_promoted_to_confirmed(request, next_reservation)

            messages.success(request, (
                f"Sua inscrição para o RAS do dia {service.date.strftime('%d/%m/%y')} "
                f"das {service.time_start.strftime('%H:%M:%S')} às {service.time_end.strftime('%H:%M:%S')} "
                "foi cancelada com sucesso."
            ))
            return redirect('my_subscriptions')

    return render(request, 'agents/confirmation_cancellation.html', {'service': service})


@permission_required('service.change_registrationservice', login_url='login')
def cancel_registration_by_manager(request, registration_pk):
    registration = get_object_or_404(RegistrationService, pk=registration_pk)
    service = registration.service
    period_pk = service.period.pk

    if request.method == 'POST':
        with transaction.atomic():
            previous_status = registration.status
            if previous_status != 'CANCELADO':
                registration.status = 'CANCELADO'
                registration.save()

                if previous_status == 'CONFIRMADO':
                    next_reservation = RegistrationService.objects.filter(
                        service=service,
                        status='RESERVA'
                    ).order_by('registration_date').first()

                    if next_reservation:
                        next_reservation.status = 'CONFIRMADO'
                        next_reservation.save()
                        notify_reservation_promoted_to_confirmed(request, next_reservation)

                messages.success(request, (
                    f"Inscrição de {registration.user.get_full_name() or registration.user.username} "
                    f"no RAS de {service.date.strftime('%d/%m/%y')} "
                    f"das {service.time_start.strftime('%H:%M:%S')} às {service.time_end.strftime('%H:%M:%S')} "
                    "foi cancelada com sucesso."
                ))
            else:
                messages.info(request, "A inscrição já estava cancelada.")

        return redirect('period_detail', pk=period_pk)

    return redirect('period_detail', pk=period_pk)


class MySubscriptionsListView(LoginRequiredMixin, ListView):
    model = RegistrationService
    paginate_by = 10
    template_name = 'agents/my_subscriptions_list.html'
    context_object_name = 'grouped_registrations'

    def get_queryset(self):
        registrations = RegistrationService.objects.filter(user=self.request.user).order_by('service__date')

        grouped_registrations = OrderedDict()
        for registration in registrations:
            month = registration.service.date.replace(day=1)
            grouped_registrations.setdefault(month, []).append(registration)

        return list(grouped_registrations.items())

@login_required
def exportar_pdf(request):
    period_id = request.GET.get('period_id')
    tipo = request.GET.get('tipo', 'todos')

    # Garantir que o período foi selecionado
    if not period_id:
        return HttpResponse("Nenhum período selecionado para exportação.", status=400)

    period = Period.objects.filter(id=period_id).first()
    if not period:
        return HttpResponse("Período não encontrado.", status=404)

    # Prefetch dos serviços e inscrições
    services_prefetch = Prefetch(
        'plantoes',
        queryset=Service.objects.prefetch_related(
            Prefetch(
                'registrations',
                queryset=RegistrationService.objects.all(),
                to_attr='all_regs'
            )
        )
    )

    # Só o período selecionado
    period = Period.objects.filter(id=period_id).prefetch_related(services_prefetch).first()

    # Agrupa services e filtra confirmados/reservas
    grouped_services = {}
    grouped_services[period] = []
    for service in period.plantoes.all():
        if tipo == 'confirmados':
            service.confirmados = [r for r in service.all_regs if r.status == 'CONFIRMADO']
            service.reservas = []
        elif tipo == 'reservas':
            service.confirmados = []
            service.reservas = [r for r in service.all_regs if r.status == 'RESERVA']
        else:
            service.confirmados = [r for r in service.all_regs if r.status == 'CONFIRMADO']
            service.reservas = [r for r in service.all_regs if r.status == 'RESERVA']
        grouped_services[period].append(service)

    # Renderiza o template
    template = get_template('exportar_lista_pdf.html')
    html_content = template.render({
        'grouped_services': grouped_services,
        'tipo': tipo,
        'now': timezone.now(),
        'period': period,  # para cabeçalho
    })

    # Gera PDF na memória (sem erros de permissão)
    pdf_file = BytesIO()
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(pdf_file)
    pdf_file.seek(0)

    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ras_{period.name}.pdf"'
    return response


@permission_required('service.view_period', login_url='login')
def relatorio_pdf_view(request):
    if request.method == 'POST':
        date_start_str = request.POST.get('date_start')
        date_end_str = request.POST.get('date_end')
        if not date_start_str or not date_end_str:
            messages.error(request, "Selecione as datas de início e fim.")
            return redirect('relatorio_pdf')

        # Converter strings para objetos date
        try:
            date_start = datetime.strptime(date_start_str, '%Y-%m-%d').date()
            date_end = datetime.strptime(date_end_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Datas inválidas.")
            return redirect('relatorio_pdf')

        # Filtrar períodos que se sobrepõem ao intervalo
        periods = Period.objects.filter(
            date_start__lte=date_end,
            date_end__gte=date_start
        ).prefetch_related(
            Prefetch('plantoes', queryset=Service.objects.prefetch_related('registrations'))
        ).order_by('date_start')

        # Coletar dados
        data = []
        for period in periods:
            period_data = {
                'period': period,
                'services': []
            }
            for service in period.plantoes.all():
                service_data = {
                    'service': service,
                    'confirmados': service.registrations.filter(status='CONFIRMADO'),
                    'reservas': service.registrations.filter(status='RESERVA'),
                    'cancelados': service.registrations.filter(status='CANCELADO'),
                }
                period_data['services'].append(service_data)
            data.append(period_data)

        # Renderizar template para PDF
        template = get_template('relatorio_pdf.html')
        now = timezone.localtime().strftime('%d/%m/%Y %H:%M:%S')
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'Logo_GCM.png')
        html_content = template.render({
            'data': data,
            'date_start': date_start,
            'date_end': date_end,
            'now': now,
            'logo_path': logo_path,
        })

        # Gerar PDF
        pdf_file = BytesIO()
        HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(pdf_file)
        pdf_file.seek(0)

        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="relatorio_{date_start}_a_{date_end}.pdf"'
        return response

    # GET: mostrar formulário
    return render(request, 'relatorio_form.html')


@permission_required('service.view_period', login_url='login')
def assinaturas_pdf(request):
    period_id = request.GET.get('period_id')
    tipo = request.GET.get('tipo', 'todos')

    # Garantir que o período foi selecionado
    if not period_id:
        return HttpResponse("Nenhum período selecionado para exportação.", status=400)

    period = Period.objects.filter(id=period_id).first()
    if not period:
        return HttpResponse("Período não encontrado.", status=404)

    # Prefetch dos serviços e inscrições
    services_prefetch = Prefetch(
        'plantoes',
        queryset=Service.objects.prefetch_related(
            Prefetch(
                'registrations',
                queryset=RegistrationService.objects.all(),
                to_attr='all_regs'
            )
        )
    )
    # Só o período selecionado
    period = Period.objects.filter(id=period_id).prefetch_related(services_prefetch).first()

    # Agrupa services e filtra confirmados/reservas
    grouped_services = {}
    grouped_services[period] = []
    for service in period.plantoes.all():
        if tipo == 'confirmados':
            service.confirmados = [r for r in service.all_regs if r.status == 'CONFIRMADO']
            service.reservas = []
        else:
            service.confirmados = [r for r in service.all_regs if r.status == 'CONFIRMADO']
        grouped_services[period].append(service)

    # Renderiza o template
    template = get_template('assinaturas_pdf.html')
    html_content = template.render({
        'grouped_services': grouped_services,
        'tipo': tipo,
        'now': timezone.now(),
        'period': period,  # para cabeçalho
    })

    # Gera PDF na memória (sem erros de permissão)
    pdf_file = BytesIO()
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(pdf_file)
    pdf_file.seek(0)

    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ras_{period.name}.pdf"'
    return response

