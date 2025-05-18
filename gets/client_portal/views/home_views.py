# client_portal/views/home_views.py
from django.views.generic import TemplateView
from django.utils import timezone

from common.models import Activite
from common.services.activite_service import ActiviteService

class HomeView(TemplateView):
    template_name = 'client_portal/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_activities'] = ActiviteService.get_upcoming_activites(6)
        return context

class AboutView(TemplateView):
    template_name = 'client_portal/about.html'

class ContactView(TemplateView):
    template_name = 'client_portal/contact.html'