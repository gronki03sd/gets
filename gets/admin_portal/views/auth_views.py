# admin_portal/views/auth_views.py
from django.views.generic import FormView, UpdateView
from django.contrib.auth.views import PasswordChangeView as BasePasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect

from common.models import User
from admin_portal.forms import AdminLoginForm, AdminPasswordChangeForm, AdminUserProfileForm
from admin_portal.mixins import AdminStaffRequiredMixin

class AdminLoginView(FormView):
    template_name = 'admin_portal/auth/login.html'
    form_class = AdminLoginForm
    success_url = reverse_lazy('admin_portal:dashboard')
    
    def form_valid(self, form):
       login(self.request, form.get_user())
       messages.success(self.request, f"Bienvenue, {form.get_user().first_name or form.get_user().username}!")
       return super().form_valid(form)
   
    def get_success_url(self):
       # Check for next parameter
       next_url = self.request.GET.get('next')
       if next_url:
           return next_url
       return self.success_url

class ProfileView(AdminStaffRequiredMixin, UpdateView):
   model = User
   form_class = AdminUserProfileForm
   template_name = 'admin_portal/auth/profile.html'
   success_url = reverse_lazy('admin_portal:profile')
   
   def get_object(self, queryset=None):
       return self.request.user
   
   def form_valid(self, form):
       response = super().form_valid(form)
       messages.success(self.request, "Votre profil a été mis à jour!")
       return response

class PasswordChangeView(AdminStaffRequiredMixin, BasePasswordChangeView):
   form_class = AdminPasswordChangeForm
   template_name = 'admin_portal/auth/change_password.html'
   success_url = reverse_lazy('admin_portal:profile')
   
   def form_valid(self, form):
       response = super().form_valid(form)
       messages.success(self.request, 'Votre mot de passe a été changé avec succès!')
       return response