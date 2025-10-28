from django.db import models
from django.conf import settings


class Period(models.Model):
    name = models.CharField(max_length=200)
    date_start = models.DateField()
    date_end = models.DateField()
    description = models.TextField(blank=True, null=True)
    date_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_start']

    def __str__(self):
        return self.name


class Service(models.Model):
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='plantoes',)
    date = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    vacancies = models.IntegerField()

    class Meta:
        ordering = ['date', 'time_start']
        unique_together = ('period', 'date', 'time_start')

    def __str__(self):
        return f"{self.period.name} - {self.date.strftime('%d/%m/%Y')} - {self.time_start.strftime('%H:%M')}"

    @property
    def occupied_vacancies(self):
        return self.registrations.filter(status='CONFIRMADO').count()

    @property
    def remaining_vacancies(self):
        return self.vacancies - self.occupied_vacancies

    @property
    def reservation_list(self):
        return self.registrations.filter(status='RESERVA').order_by('date_vacancie')


class RegistrationService(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMADO', 'Confirmado'),
        ('RESERVA', 'Reserva'),
        ('CANCELADO', 'Cancelado'),
    )

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='registrations', verbose_name="Plantão")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_services', verbose_name="Usuário")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='RESERVA', verbose_name="Status da Vaga")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Data de Inscrição")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('service', 'user')
        ordering = ['service', 'registration_date']
        verbose_name = "Inscrição em Plantão"
        verbose_name_plural = "Inscrições em Plantões"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.service} ({self.get_status_display()})"
