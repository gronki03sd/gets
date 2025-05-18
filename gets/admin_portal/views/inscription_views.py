# admin_portal/views/inscription_views.py
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

from common.models import Inscription
from common.forms.inscription_forms import InscriptionForm
from common.services.inscription_service import InscriptionService
from admin_portal.mixins import AdminStaffRequiredMixin

class InscriptionCreateView(AdminStaffRequiredMixin, CreateView):
    model = Inscription
    form_class = InscriptionForm
    template_name = 'admin_portal/inscriptions/create.html'
    
    def get_initial(self):
        initial = super().get_initial()
        # Pre-populate with activity or participant if provided in URL
        if 'activite_id' in self.request.GET:
            initial['activite'] = self.request.GET['activite_id']
        if 'participant_id' in self.request.GET:
            initial['participant'] = self.request.GET['participant_id']
        return initial
    
    def form_valid(self, form):
        try:
            participant_id = form.cleaned_data['participant'].id
            activite_id = form.cleaned_data['activite'].id
            statut = form.cleaned_data['statut']
            
            inscription = InscriptionService.create_inscription(
                participant_id, activite_id, statut, self.request.user
            )
            
            participant = inscription.participant
            activite = inscription.activite
            messages.success(self.request, f"Inscription de {participant} à {activite} réussie!")
            
            # Redirect based on context
            if 'activite_id' in self.request.POST:
                return redirect('admin_portal:activite_detail', pk=activite_id)
            else:
                return redirect('admin_portal:participant_detail', pk=participant_id)
                
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

class InscriptionUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = Inscription
    form_class = InscriptionForm
    template_name = 'admin_portal/inscriptions/edit.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:activite_detail', kwargs={'pk': self.object.activite.pk})
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Inscription modifiée avec succès!")
        return redirect(self.get_success_url())

class InscriptionDeleteView(AdminStaffRequiredMixin, DeleteView):
    model = Inscription
    template_name = 'admin_portal/inscriptions/delete.html'
    context_object_name = 'inscription'
    
    def get_success_url(self):
        # Remember the activite before deletion
        self.activite_pk = self.object.activite.pk
        self.participant_pk = self.object.participant.pk
        
        # Determine redirect destination based on referrer
        referer = self.request.META.get('HTTP_REFERER', '')
        if referer and 'participant' in referer:
            return reverse_lazy('admin_portal:participant_detail', kwargs={'pk': self.participant_pk})
        else:
            return reverse_lazy('admin_portal:activite_detail', kwargs={'pk': self.activite_pk})
    
    def delete(self, request, *args, **kwargs):
        inscription = self.get_object()
        success_url = self.get_success_url()
        
        participant_name = f"{inscription.participant.prenom} {inscription.participant.nom}"
        activite_name = inscription.activite.nom
        
        InscriptionService.delete_inscription(inscription.id)
        messages.success(request, f"Inscription de {participant_name} à {activite_name} supprimée!")
        
        return redirect(success_url)