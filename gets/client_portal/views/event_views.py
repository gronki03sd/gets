# client_portal/views/event_views.py
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone

from common.models import Activite, Participant
from common.services.activite_service import ActiviteService
from common.services.inscription_service import InscriptionService

class EventListView(ListView):
    model = Activite
    template_name = 'client_portal/events/list.html'
    context_object_name = 'activities'
    
    def get_queryset(self):
        # Get search parameters
        search_query = self.request.GET.get('search', '')
        date_filter = self.request.GET.get('date', '')
        
        # Filter for future events
        return ActiviteService.search_activites(
            query=search_query, 
            date_debut=date_filter if date_filter else None
        ).filter(date_debut__gte=timezone.now())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['date_filter'] = self.request.GET.get('date', '')
        return context

class EventDetailView(DetailView):
    model = Activite
    template_name = 'client_portal/events/detail.html'
    context_object_name = 'activity'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if the user can register (if logged in and has participant info)
        can_register = False
        user_already_registered = False
        
        if self.request.user.is_authenticated:
            # Check if user has participant information linked
            participant = None
            try:
                # Try to find a participant record that matches the user's information
                participant = Participant.objects.filter(
                    email=self.request.user.email
                ).first()
                
                if participant:
                    can_register = True
                    # Check if already registered for this activity
                    user_already_registered = participant.est_inscrit(self.object)
            except:
                can_register = False
        
        context['can_register'] = can_register
        context['user_already_registered'] = user_already_registered
        
        return context

class EventRegisterView(LoginRequiredMixin, FormView):
    template_name = 'client_portal/events/register.html'
    form_class = None  # No form needed for this view
    success_url = reverse_lazy('client_portal:dashboard')
    
    def get(self, request, *args, **kwargs):
        # Direct GET requests should be redirected to the event detail page
        return redirect('client_portal:event_detail', pk=self.kwargs['pk'])
    
    def post(self, request, *args, **kwargs):
        activite_id = self.kwargs['pk']
        
        try:
            inscription = InscriptionService.client_register_for_event(request.user, activite_id)
            activite = inscription.activite
            messages.success(request, f"Vous êtes inscrit avec succès à l'activité: {activite.nom}")
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('client_portal:event_detail', pk=activite_id)
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite lors de l'inscription: {str(e)}")
            return redirect('client_portal:event_detail', pk=activite_id)
        
        return redirect(self.success_url)