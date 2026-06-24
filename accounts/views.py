from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.db.models import Q
from .forms import RegisterForm, UpdateUserForm, TemporaryPasswordForm
from . import models
User = get_user_model()


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


@permission_required('accounts.change_customuser', login_url='login')
def reset_temporary_password(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = TemporaryPasswordForm(request.POST)
        if form.is_valid():
            temporary_password = form.cleaned_data['temporary_password']
            user.set_password(temporary_password)
            user.must_change_password = True
            user.save()
            messages.success(request, f"Senha temporária criada para {user.username}. O usuário deverá alterá-la no próximo login.")
            return redirect('detail_servidor', pk=user.pk)
    else:
        form = TemporaryPasswordForm()

    return render(request, 'temporary_password_form.html', {'form': form, 'user': user})


class ForcePasswordChangeView(FormView):
    template_name = 'registration/force_password_change.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        user.must_change_password = False
        user.save()
        messages.success(self.request, "Senha alterada com sucesso!")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.must_change_password:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


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
    form_class = UpdateUserForm
    success_url = reverse_lazy('list_servidor')


class DeleteServidor(DeleteView):
    model = models.CustomUser
    template_name = 'delete_servidor.html'
    context_object_name = 'servidor'
    success_url = reverse_lazy ('list_servidor')
