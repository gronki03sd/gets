# common/services/activite_service.py
from django.db.models import Q, Count
from django.utils import timezone
from common.models import Activite

class ActiviteService:
    @staticmethod
    def get_all_activites():
        return Activite.objects.all()
    
    @staticmethod
    def get_activite_by_id(activite_id):
        try:
            return Activite.objects.get(pk=activite_id)
        except Activite.DoesNotExist:
            return None
    
    @staticmethod
    def search_activites(query=None, date_debut=None):
        activites = Activite.objects.all()
        
        if query:
            activites = activites.filter(
                Q(nom__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if date_debut:
            activites = activites.filter(date_debut__date=date_debut)
        
        return activites
    
    @staticmethod
    def get_upcoming_activites(limit=None):
        activites = Activite.objects.filter(
            date_debut__gte=timezone.now()
        ).order_by('date_debut')
        
        if limit:
            activites = activites[:limit]
            
        return activites
    
    @staticmethod
    def get_popular_activites(limit=5):
        return Activite.objects.annotate(
            nombre_inscrits=Count('inscriptions')
        ).order_by('-nombre_inscrits')[:limit]
    
    @staticmethod
    def create_activite(form_data, user):
        activite = form_data.save(commit=False)
        activite.created_by = user
        activite.save()
        
        # For many-to-many fields
        form_data.save_m2m()
        return activite
    
    @staticmethod
    def update_activite(activite_id, form_data):
        activite = form_data.save()
        return activite
    
    @staticmethod
    def delete_activite(activite_id):
        activite = Activite.objects.get(pk=activite_id)
        activite.delete()
        return True