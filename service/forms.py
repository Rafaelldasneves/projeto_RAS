from django import forms
from django.forms.models import inlineformset_factory
from .models import Period, Service


class PeriodForm(forms.ModelForm):
    """
    Formulário para a criação do objeto Periodo.
    """
    class Meta:
        model = Period
        fields = ['name', 'date_start', 'date_end', 'description']
        widgets = {
            'date_start': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'date_end': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'name': 'Título',
            'date_start': 'Data Inicio',
            'date_end': 'Data Término',
            'description': 'Descrição',
        }


class ServiceForm(forms.ModelForm):
    """
    Formulário para a criação individual de um Plantão.
    Usado como base para o Formset.
    """
    class Meta:
        model = Service
        fields = ['date', 'time_start', 'time_end', 'vacancies']
        widgets = {
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'time_start': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'time_end': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'vacancies': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
        }
        labels = {
            'date': 'Data',
            'time_start': 'Inicio',
            'time_end': 'Término',
            'vacancies': 'Vagas',
        }


ServiceInlineFormSet = inlineformset_factory(
    parent_model=Period,
    model=Service,
    form=ServiceForm,
    extra=0,
    min_num=1,
    can_delete=True,
)
