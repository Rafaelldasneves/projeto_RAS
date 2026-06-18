from django import forms
from .models import Service


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
            'time_start': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'step': '60', 'class': 'form-control'}),
            'time_end': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'step': '60', 'class': 'form-control'}),
            'vacancies': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
        }
        labels = {
            'date': 'Data',
            'time_start': 'Inicio',
            'time_end': 'Término',
            'vacancies': 'Vagas',
        }
