# admin_portal/views/dashboard_views.py
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate

from common.models import Participant, Activite, Inscription
from common.services.activite_service import ActiviteService
from admin_portal.mixins import AdminStaffRequiredMixin

class DashboardView(AdminStaffRequiredMixin, TemplateView):
    template_name = 'admin_portal/dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques de base
        context['total_participants'] = Participant.objects.count()
        context['total_activites'] = Activite.objects.count()
        context['total_inscriptions'] = Inscription.objects.count()
        
        # Activités à venir
        context['activites_a_venir'] = ActiviteService.get_upcoming_activites(5)
        
        # Activités populaires
        context['activites_populaires'] = ActiviteService.get_popular_activites(5)
        
        # Derniers participants inscrits
        context['recent_participants'] = Participant.objects.order_by('-date_inscription')[:5]
        
        # Statistiques par jour (pour graphique)
        inscriptions_par_jour = Inscription.objects.annotate(
            date=TruncDate('date_inscription')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')[:14]  # 2 dernières semaines
        
        context['inscriptions_par_jour'] = list(inscriptions_par_jour)
        
        return context