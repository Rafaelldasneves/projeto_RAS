from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from . import models

from django.contrib.auth import get_user_model
from django.db.models import Q
User = get_user_model()

from accounts.forms import RegisterForm


class RegisterUserView(CreateView):
    model = User
    template_name = 'registration/register_servidor.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')
    success_message = "Usuário cadastrado com sucesso!"

    def form_valid(self, form):
        password = form.cleaned_data.get('password')
        if password:
            form.instance.set_password(password)
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ListServidor(ListView):
    model = models.CustomUser
    template_name = 'list_servidor.html'
    context_object_name = "servidores"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        order_by = self.request.GET.get('order_by', 'username')
        
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q) | Q(registration__icontains=q)
            )
        
        # Para alternar asc/desc
        direction = self.request.GET.get('direction', 'asc')
        if direction == 'desc':
            order_by = '-' + order_by
        
        queryset = queryset.order_by(order_by)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['order_by'] = self.request.GET.get('order_by', 'username')
        context['direction'] = self.request.GET.get('direction', 'asc')
        return context


class DetailServidor(DetailView):
    model = models.CustomUser
    template_name = 'detail_servidor.html'


class UpdateServidor(UpdateView):
    model = models.CustomUser
    template_name= 'update_servidor.html'
    form_class = RegisterForm
    success_url = reverse_lazy ('list_servidor')


class DeleteServidor(DeleteView):
    model = models.CustomUser
    template_name = 'delete_servidor.html'
    context_object_name = 'servidor'
    success_url = reverse_lazy ('list_servidor')