from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'registration',
        'username',
        'name',
        'position',
        'is_active',
    )

    search_fields = (
        'username',
        'name',
        'registration',
    )

    list_filter = (
        'position',
        'is_active',
    )

    ordering = (
        'registration',
    )

    fieldsets = (
        (
            'Dados Funcionais',
            {
                'fields': (
                    'position',
                    'registration',
                    'admission_date',
                )
            }
        ),
        (
            'Dados Pessoais',
            {
                'fields': (
                    'name',
                    'email',
                    'phone_number',
                )
            }
        ),
        (
            'Acesso',
            {
                'fields': (
                    'username',
                    'password',
                )
            }
        ),
        (
            'Permissões',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            }
        ),
    )