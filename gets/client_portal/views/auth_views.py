# client_portal/views/auth_views.py
from django.views.generic import CreateView, FormView, RedirectView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.shortcuts import redirect

from common.models import User
from client_portal.forms import ClientRegisterForm, ClientLoginForm

class ClientRegisterView(CreateView):
    model = User
    form_class = ClientRegisterForm
    template_name = 'client_portal/register.html'
    success_url = reverse_lazy('client_portal:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Votre compte a été créé avec succès! Vous pouvez maintenant vous connecter.")
        return response

class ClientLoginView(FormView):
    form_class = ClientLoginForm
    template_name = 'client_portal/login.html'
    success_url = reverse_lazy('client_portal:dashboard')
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f"Bienvenue, {user.first_name or user.username}!")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Nom d'utilisateur ou mot de passe incorrect.")
            return self.form_invalid(form)

class ClientLogoutView(RedirectView):
    url = reverse_lazy('client_portal:home')
    
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Vous êtes déconnecté.")
        return super().get(request, *args, **kwargs)