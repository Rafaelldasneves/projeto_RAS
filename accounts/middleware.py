from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.shortcuts import redirect
from django.urls import resolve
from django.urls.exceptions import Resolver404
from .models import LoggedInUser

User = get_user_model()


class OneSessionPerUserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            current_session_key = request.session.session_key

            obj, created = LoggedInUser.objects.get_or_create(
                user=request.user
            )

            if obj.session_key:
                if obj.session_key != current_session_key:
                    Session.objects.filter(
                        session_key=obj.session_key
                    ).delete()

            obj.session_key = current_session_key
            obj.save()

        return self.get_response(request)


class ForcePasswordChangeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_view_names = {
            'force_password_change',
            'login',
            'logout',
        }

    def __call__(self, request):
        if request.user.is_authenticated:
            # Recarregar o usuário do banco de dados para obter valores atualizados
            request.user = User.objects.get(pk=request.user.pk)
            # Verificar se o usuário deve obrigatoriamente alterar a senha
            if request.user.must_change_password:
                path = request.path_info
                # URLs estáticas e admin são sempre permitidas
                if (
                    path.startswith(settings.STATIC_URL) or path.startswith(getattr(settings, 'MEDIA_URL', '/media/')) or path.startswith('/admin/')
                    ):
                    return self.get_response(request)                
                # Tentar resolver a view para o path atual
                try:
                    match = resolve(path)
                    view_name = match.url_name                    
                    # Se a view não está na lista de permitidas, redirecionar
                    if view_name not in self.allowed_view_names:
                        return redirect('force_password_change')
                except Resolver404:
                    # Se não conseguir resolver, deixar passar
                    pass

        return self.get_response(request)