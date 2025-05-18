# admin_portal/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages  # Add this import for messages

class AdminStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verify that the current user is authenticated and has admin access."""
    login_url = reverse_lazy('admin_portal:login')
    
    def test_func(self):
        """Check if user has appropriate role."""
        return self.request.user.is_authenticated and (
            self.request.user.is_admin or 
            self.request.user.is_manager or 
            self.request.user.is_staff or
            self.request.user.is_superuser
        )
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        
        # If user is logged in but doesn't have permission, redirect to client portal
        messages.error(self.request, "Vous n'avez pas accès à cette section.")
        return redirect('client_portal:home')

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verify that the current user is authenticated and is an admin."""
    login_url = reverse_lazy('admin_portal:login')
    
    def test_func(self):
        """Check if user is admin."""
        return self.request.user.is_authenticated and (
            self.request.user.is_admin or 
            self.request.user.is_superuser
        )
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        
        # If user is logged in but doesn't have admin rights
        messages.error(self.request, "Cette action nécessite des privilèges d'administrateur.")
        return redirect('admin_portal:dashboard')

class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verify that the current user is authenticated and is a manager or admin."""
    login_url = reverse_lazy('admin_portal:login')
    
    def test_func(self):
        """Check if user is manager or admin."""
        return self.request.user.is_authenticated and (
            self.request.user.is_manager or 
            self.request.user.is_admin or 
            self.request.user.is_superuser
        )
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        
        # If user is logged in but doesn't have manager rights
        messages.error(self.request, "Cette action nécessite des privilèges de gestionnaire.")
        return redirect('admin_portal:dashboard')