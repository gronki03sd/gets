# common/services/animateur_service.py
from django.db.models import Q
from common.models import Animateur, Activite

class AnimateurService:
    @staticmethod
    def get_all_animateurs():
        return Animateur.objects.all()
    
    @staticmethod
    def get_animateur_by_id(animateur_id):
        try:
            return Animateur.objects.get(pk=animateur_id)
        except Animateur.DoesNotExist:
            return None
    
    @staticmethod
    def search_animateurs(query=None):
        if not query:
            return Animateur.objects.all()
        
        return Animateur.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(email__icontains=query) |
            Q(competence__icontains=query)
        )
    
    @staticmethod
    def create_animateur(form_data, user):
        animateur = form_data.save(commit=False)
        animateur.created_by = user
        animateur.save()
        return animateur
    
    @staticmethod
    def update_animateur(animateur_id, form_data):
        animateur = form_data.save()
        return animateur
    
    @staticmethod
    def delete_animateur(animateur_id):
        animateur = Animateur.objects.get(pk=animateur_id)
        
        # Optional: Handle related activites (remove animateur from activities)
        # for activite in Activite.objects.filter(animateurs=animateur):
        #     activite.animateurs.remove(animateur)
        
        animateur.delete()
        return True
    
    @staticmethod
    def get_activities_by_animateur(animateur_id):
        """Get all activities assigned to this animateur"""
        animateur = Animateur.objects.get(pk=animateur_id)
        return animateur.activites.all()
    
    @staticmethod
    def assign_to_activity(animateur_id, activite_id):
        """Assign animateur to an activity"""
        animateur = Animateur.objects.get(pk=animateur_id)
        activite = Activite.objects.get(pk=activite_id)
        
        # Check if already assigned
        if activite.animateurs.filter(pk=animateur_id).exists():
            return False
        
        activite.animateurs.add(animateur)
        return True
    
    @staticmethod
    def remove_from_activity(animateur_id, activite_id):
        """Remove animateur from an activity"""
        animateur = Animateur.objects.get(pk=animateur_id)
        activite = Activite.objects.get(pk=activite_id)
        
        if not activite.animateurs.filter(pk=animateur_id).exists():
            return False
        
        activite.animateurs.remove(animateur)
        return True