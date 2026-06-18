from django.db import models


class Period(models.Model):
    name = models.CharField(max_length=200)
    date_start = models.DateField()
    date_end = models.DateField()
    description = models.TextField(blank=True, null=True)
    available_from = models.DateTimeField(blank=True, null=True, help_text='Data e hora em que o período passa a ficar visível para usuários.')
    available_until = models.DateTimeField(blank=True, null=True, help_text='Data e hora em que o período deixa de ficar visível para usuários.')
    date_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_start']

    def __str__(self):
        return self.name
