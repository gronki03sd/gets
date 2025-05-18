# client_portal/views/account_views.py
from django.views.generic import TemplateView, UpdateView, FormView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone

from common.models import Participant, Inscription, User,Activite
from common.forms.participant_forms import ParticipantForm
from common.forms.user_forms import UserProfileForm
from common.services.inscription_service import InscriptionService

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'client_portal/account/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Try to find participant based on user email
        participant = None
        inscriptions = []
        
        try:
            participant = Participant.objects.filter(email=self.request.user.email).first()
            if participant:
                inscriptions = Inscription.objects.filter(participant=participant)
        except:
            pass
        
        # Get upcoming activities
        upcoming_activities = Activite.objects.filter(
            date_debut__gte=timezone.now()
        ).order_by('date_debut')[:3]
        
        context['participant'] = participant
        context['inscriptions'] = inscriptions
        context['upcoming_activities'] = upcoming_activities
        
        return context

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'client_portal/account/profile.html'
    success_url = reverse_lazy('client_portal:profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Update participant info if exists
        participant = Participant.objects.filter(email=self.request.user.email).first()
        if participant:
            participant.nom = self.request.user.last_name
            participant.prenom = self.request.user.first_name
            participant.email = self.request.user.email
            participant.telephone = self.request.user.phone_number
            participant.save()
        
        messages.success(self.request, "Votre profil a été mis à jour.")
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if the user has a participant record
        context['has_participant'] = Participant.objects.filter(
            email=self.request.user.email
        ).exists()
        return context

class ParticipantInfoView(LoginRequiredMixin, UpdateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'client_portal/account/participant_form.html'
    success_url = reverse_lazy('client_portal:profile')
    
    def get_object(self, queryset=None):
        # Find existing participant or return None to create new one
        return Participant.objects.filter(email=self.request.user.email).first()
    
    def form_valid(self, form):
        participant = form.save(commit=False)
        
        # Link to the current user
        if not participant.email:
            participant.email = self.request.user.email
        if not participant.created_by:
            participant.created_by = self.request.user
            
        participant.save()
        messages.success(self.request, "Vos informations de participant ont été mises à jour.")
        return redirect(self.success_url)
    
    def get_initial(self):
        # Pre-fill with user info if creating new participant
        initial = super().get_initial()
        if not self.get_object():
            initial.update({
                'nom': self.request.user.last_name,
                'prenom': self.request.user.first_name,
                'email': self.request.user.email,
                'telephone': self.request.user.phone_number
            })
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = self.get_object() is None
        return context

class CancelRegistrationView(LoginRequiredMixin, DeleteView):
    model = Inscription
    template_name = 'client_portal/booking/cancel.html'
    success_url = reverse_lazy('client_portal:dashboard')
    context_object_name = 'inscription'
    
    def get_object(self, queryset=None):
        inscription_id = self.kwargs.get('inscription_id')
        inscription = get_object_or_404(Inscription, id=inscription_id)
        
        # Security check - make sure the logged in user owns this registration
        participant = Participant.objects.filter(email=self.request.user.email).first()
        if not participant or inscription.participant != participant:
            messages.error(self.request, "Vous n'êtes pas autorisé à annuler cette inscription.")
            return None
            
        return inscription
    
    def delete(self, request, *args, **kwargs):
        inscription = self.get_object()
        if not inscription:
            return redirect(self.success_url)
            
        try:
            InscriptionService.cancel_inscription(inscription.id)
            messages.success(request, f"Votre inscription à {inscription.activite.nom} a été annulée.")
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
            
        return redirect(self.success_url)