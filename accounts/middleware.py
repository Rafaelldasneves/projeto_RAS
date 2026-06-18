from django.contrib.sessions.models import Session
from .models import LoggedInUser


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