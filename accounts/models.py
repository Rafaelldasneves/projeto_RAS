from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    POSITION_CHOICES = [
        ('GCM', 'Guarda Civil Municipal'),
        ('GPCM', 'Guarda Patrimonial Civil Municipal'),
    ]

    position = models.CharField ('Cargo', max_length=5, choices=POSITION_CHOICES, blank=True, null=True)
    username = models.CharField ("Nome de Guerra", max_length=20, unique=True)
    registration = models.CharField ("Matricula", max_length=5, unique=True, blank=True, null=True)
    name = models.CharField ("Nome Completo", max_length=100, blank=True, null=True)
    admission_date = models.DateField ("Data de Admissão", blank=True, null=True)
    email = models.EmailField("E-mail", blank=True, null=True)
    phone_number = models.CharField ("Telefone", max_length=15, blank=True, null=True)
    must_change_password = models.BooleanField(
        default=False,
        verbose_name='Obrigar troca de senha'
    )


User = get_user_model()

class LoggedInUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.user.username
    