# common/services/search_service.py
from django.db.models import Q
from common.models import Participant, Activite, Responsable, Animateur, Infrastructure, Materiel

class SearchService:
    @staticmethod
    def search_all(query):
        """Search across all entity types"""
        results = {}
        
        if not query:
            return results
            
        results['participants'] = SearchService.search_participants(query)
        results['activites'] = SearchService.search_activites(query)
        results['responsables'] = SearchService.search_responsables(query)
        results['animateurs'] = SearchService.search_animateurs(query)
        results['infrastructures'] = SearchService.search_infrastructures(query)
        results['materiels'] = SearchService.search_materiels(query)
        
        return results
    
    @staticmethod
    def search_by_type(query, entity_type):
        """Search for specific entity type"""
        if entity_type == 'participants':
            return {'participants': SearchService.search_participants(query)}
        elif entity_type == 'activites':
            return {'activites': SearchService.search_activites(query)}
        elif entity_type == 'responsables':
            return {'responsables': SearchService.search_responsables(query)}
        elif entity_type == 'animateurs':
            return {'animateurs': SearchService.search_animateurs(query)}
        elif entity_type == 'infrastructures':
            return {'infrastructures': SearchService.search_infrastructures(query)}
        elif entity_type == 'materiels':
            return {'materiels': SearchService.search_materiels(query)}
        else:
            return SearchService.search_all(query)
    
    @staticmethod
    def search_participants(query):
        return Participant.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(email__icontains=query) |
            Q(telephone__icontains=query)
        )
    
    @staticmethod
    def search_activites(query):
        return Activite.objects.filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query)
        )
    
    @staticmethod
    def search_responsables(query):
        return Responsable.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(email__icontains=query) |
            Q(specialite__icontains=query)
        )
    
    @staticmethod
    def search_animateurs(query):
        return Animateur.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(email__icontains=query) |
            Q(competence__icontains=query)
        )
    
    @staticmethod
    def search_infrastructures(query):
        return Infrastructure.objects.filter(
            Q(nom__icontains=query) | 
            Q(type__icontains=query) |
            Q(localisation__icontains=query)
        )
    
    @staticmethod
    def search_materiels(query):
        return Materiel.objects.filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query)
        )