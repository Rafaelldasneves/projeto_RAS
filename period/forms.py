from django import forms
from django.forms.models import inlineformset_factory
from .models import Period
from service.models import Service


class PeriodForm(forms.ModelForm):

    class Meta:
        model = Period
        fields = ['name', 'date_start', 'date_end', 'available_from', 'available_until', 'description']
        widgets = {
            'date_start': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'date_end': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'available_from': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'available_until': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'name': 'Título',
            'date_start': 'Data Início',
            'date_end': 'Data Término',
            'available_from': 'Disponível a partir de',
            'available_until': 'Disponível até',
            'description': 'Descrição',
        }


class ServiceForm(forms.ModelForm):

    class Meta:
        model = Service
        fields = ['date', 'time_start', 'time_end', 'vacancies']
        widgets = {
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'time_start': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'step': '1', 'class': 'form-control'}),
            'time_end': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'step': '1', 'class': 'form-control'}),
            'vacancies': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
        }
        labels = {
            'date': 'Data',
            'time_start': 'Inicio',
            'time_end': 'Término',
            'vacancies': 'Numero de Vagas',
        }


ServiceInlineFormSet = inlineformset_factory(
    parent_model=Period,
    model=Service,
    form=ServiceForm,
    extra=0,
    min_num=1,
    can_delete=True,
)
