from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from django import forms
from .models import Period
from .forms import PeriodForm, ServiceInlineFormSet, ServiceForm
from service.models import Service


@permission_required('period.add_period', login_url='login')
def PeriodCreate(request):
    if request.method == 'POST':
        form = PeriodForm(request.POST)
        if form.is_valid():
            period = form.save(commit=False)
            formset = ServiceInlineFormSet(request.POST, instance=period)
            if formset.is_valid():
                try:
                    with transaction.atomic():
                        period.save()
                        formset.save()
                    messages.success(request, "Período e RAS criados com sucesso!")
                    return redirect('period_list')
                except Exception as e:
                    messages.error(request, f"Ocorreu um erro ao salvar: {e}")
            else:
                messages.error(request, "Erro de validação. Verifique os dados inseridos no RAS.")
        else:
            formset = ServiceInlineFormSet(request.POST, instance=Period())
            messages.error(request, "Erro de validação. Verifique os dados inseridos no período.")

    else:
        form = PeriodForm()
        formset = ServiceInlineFormSet(instance=Period())
    context = {
        'form': form,
        'formset': formset,
        'title': 'Criar Novo Período de Plantões'
    }
    return render(request, 'period_create.html', context)


class PeriodListView(LoginRequiredMixin, ListView):
    model = Period
    template_name = 'period_list.html'
    context_object_name = 'periods'
    paginate_by = 10


class PeriodDetailView(LoginRequiredMixin, DetailView):
    model = Period
    template_name = 'period_detail.html'
    paginate_by = 10
    context_object_name = 'period'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = list(self.object.plantoes.prefetch_related('registrations__user').order_by('date', 'time_start'))
        for service in services:
            registrations = service.registrations.all()
            service.confirmados = registrations.filter(status='CONFIRMADO')
            service.reservas = registrations.filter(status='RESERVA')
            service.cancelados = registrations.filter(status='CANCELADO')
        context['services'] = services
        context['total_vacancies'] = sum(service.vacancies for service in services)
        return context


class PeriodUpdateView(LoginRequiredMixin, UpdateView):
    model = Period
    form_class = PeriodForm
    template_name = 'period_update.html'
    success_url = reverse_lazy('period_list')
    success_message = "RAS atualizados com sucesso!"

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


class PeriodDeleteView(LoginRequiredMixin, DeleteView):
    model = Period
    success_url = reverse_lazy('period_list')
    template_name = 'period_delete.html'

    def get_success_url(self):
        from django.contrib import messages
        messages.success(self.request, "O Período e todos os RAS associados foram excluídos permanentemente.")
        return reverse_lazy('period_list')
