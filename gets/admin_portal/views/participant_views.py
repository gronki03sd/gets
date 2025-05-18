# admin_portal/views/participant_views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from common.models import Participant
from common.forms.participant_forms import ParticipantForm
from common.services.participant_service import ParticipantService
from admin_portal.mixins import AdminStaffRequiredMixin

class ParticipantListView(AdminStaffRequiredMixin, ListView):
    model = Participant
    template_name = 'admin_portal/participants/list.html'
    context_object_name = 'participants'
    
    def get_queryset(self):
        search_query = self.request.GET.get('q', '')
        return ParticipantService.search_participants(search_query)

class ParticipantDetailView(AdminStaffRequiredMixin, DetailView):
    model = Participant
    template_name = 'admin_portal/participants/detail.html'
    context_object_name = 'participant'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inscriptions'] = self.object.inscriptions.all()
        return context

class ParticipantCreateView(AdminStaffRequiredMixin, CreateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'admin_portal/participants/create.html'
    success_url = reverse_lazy('admin_portal:participant_list')
    
    def form_valid(self, form):
        participant = ParticipantService.create_participant(form, self.request.user)
        messages.success(self.request, f"Participant {participant} ajouté avec succès!")
        return redirect(self.success_url)

class ParticipantUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'admin_portal/participants/edit.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:participant_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        participant = ParticipantService.update_participant(self.object.pk, form)
        messages.success(self.request, f"Participant {participant} modifié avec succès!")
        return redirect(self.get_success_url())

class ParticipantDeleteView(AdminStaffRequiredMixin, DeleteView):
    model = Participant
    template_name = 'admin_portal/participants/delete.html'
    success_url = reverse_lazy('admin_portal:participant_list')
    context_object_name = 'participant'
    
    def delete(self, request, *args, **kwargs):
        participant = self.get_object()
        message = f"Participant {participant} supprimé avec succès!"
        ParticipantService.delete_participant(participant.pk)
        messages.success(self.request, message)
        return redirect(self.success_url)

# This function would handle HTMX ajax search
from django.shortcuts import render

def participant_search(request):
    search_query = request.GET.get('q', '')
    participants = ParticipantService.search_participants(search_query)
    return render(request, 'admin_portal/participants/partials/participant_list.html', {'participants': participants})