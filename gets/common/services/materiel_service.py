# common/services/materiel_service.py
from django.db.models import Q, Sum
from common.models import Materiel, Activite, ActiviteMateriel

class MaterielService:
    @staticmethod
    def get_all_materiels():
        return Materiel.objects.all()
    
    @staticmethod
    def get_materiel_by_id(materiel_id):
        try:
            return Materiel.objects.get(pk=materiel_id)
        except Materiel.DoesNotExist:
            return None
    
    @staticmethod
    def search_materiels(query=None):
        if not query:
            return Materiel.objects.all()
        
        return Materiel.objects.filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query)
        )
    
    @staticmethod
    def create_materiel(form_data, user):
        materiel = form_data.save(commit=False)
        materiel.created_by = user
        materiel.save()
        return materiel
    
    @staticmethod
    def update_materiel(materiel_id, form_data):
        materiel = form_data.save()
        return materiel
    
    @staticmethod
    def delete_materiel(materiel_id):
        materiel = Materiel.objects.get(pk=materiel_id)
        materiel.delete()
        return True
    
    @staticmethod
    def update_quantite(materiel_id, new_quantity):
        """Update materiel quantity"""
        materiel = Materiel.objects.get(pk=materiel_id)
        materiel.quantite_disponible = new_quantity
        materiel.save()
        return materiel
    
    @staticmethod
    def increment_quantite(materiel_id, amount=1):
        """Increment materiel quantity"""
        materiel = Materiel.objects.get(pk=materiel_id)
        materiel.quantite_disponible += amount
        materiel.save()
        return materiel
    
    @staticmethod
    def decrement_quantite(materiel_id, amount=1):
        """Decrement materiel quantity"""
        materiel = Materiel.objects.get(pk=materiel_id)
        if materiel.quantite_disponible >= amount:
            materiel.quantite_disponible -= amount
            materiel.save()
            return materiel
        else:
            raise ValueError(f"Quantité insuffisante pour {materiel.nom}")
    
    @staticmethod
    def get_activities_by_materiel(materiel_id):
        """Get all activities using this materiel"""
        materiel = Materiel.objects.get(pk=materiel_id)
        return materiel.activites.all()
    
    @staticmethod
    def assign_to_activity(materiel_id, activite_id, quantite_requise=1):
        """Assign materiel to an activity with required quantity"""
        materiel = Materiel.objects.get(pk=materiel_id)
        activite = Activite.objects.get(pk=activite_id)
        
        # Check if already assigned
        activity_materiel = ActiviteMateriel.objects.filter(
            materiel_id=materiel_id, 
            activite_id=activite_id
        ).first()
        
        if activity_materiel:
            # Update quantity if already assigned
            activity_materiel.quantite_requise = quantite_requise
            activity_materiel.save()
        else:
            # Create new relationship
            ActiviteMateriel.objects.create(
                materiel=materiel,
                activite=activite,
                quantite_requise=quantite_requise
            )
        
        return True
    
    @staticmethod
    def remove_from_activity(materiel_id, activite_id):
        """Remove materiel from an activity"""
        try:
            activity_materiel = ActiviteMateriel.objects.get(
                materiel_id=materiel_id, 
                activite_id=activite_id
            )
            activity_materiel.delete()
            return True
        except ActiviteMateriel.DoesNotExist:
            return False
    
    @staticmethod
    def check_disponibilite(materiel_id, date_debut, date_fin, quantite=1):
        """Check if materiel is available for a specific time slot"""
        materiel = Materiel.objects.get(pk=materiel_id)
        
        # Get total quantity required for other activities during this time slot
        from django.db.models import F
        reserved_quantity = ActiviteMateriel.objects.filter(
            materiel_id=materiel_id,
            activite__date_debut__lt=date_fin,
            activite__date_fin__gt=date_debut
        ).aggregate(total=Sum('quantite_requise'))['total'] or 0
        
        # Check if enough quantity available
        return materiel.quantite_disponible - reserved_quantity >= quantite