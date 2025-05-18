# common/services/infrastructure_service.py
from django.db.models import Q
from common.models import Infrastructure, Activite

class InfrastructureService:
    @staticmethod
    def get_all_infrastructures():
        return Infrastructure.objects.all()
    
    @staticmethod
    def get_infrastructure_by_id(infrastructure_id):
        try:
            return Infrastructure.objects.get(pk=infrastructure_id)
        except Infrastructure.DoesNotExist:
            return None
    
    @staticmethod
    def search_infrastructures(query=None, disponible_only=False):
        infrastructures = Infrastructure.objects.all()
        
        if query:
            infrastructures = infrastructures.filter(
                Q(nom__icontains=query) | 
                Q(type__icontains=query) |
                Q(localisation__icontains=query)
            )
        
        if disponible_only:
            infrastructures = infrastructures.filter(disponible=True)
        
        return infrastructures
    
    @staticmethod
    def create_infrastructure(form_data, user):
        infrastructure = form_data.save(commit=False)
        infrastructure.created_by = user
        infrastructure.save()
        return infrastructure
    
    @staticmethod
    def update_infrastructure(infrastructure_id, form_data):
        infrastructure = form_data.save()
        return infrastructure
    
    @staticmethod
    def delete_infrastructure(infrastructure_id):
        infrastructure = Infrastructure.objects.get(pk=infrastructure_id)
        infrastructure.delete()
        return True
    
    @staticmethod
    def set_disponibilite(infrastructure_id, disponible):
        """Update availability status"""
        infrastructure = Infrastructure.objects.get(pk=infrastructure_id)
        infrastructure.disponible = disponible
        infrastructure.save()
        return infrastructure
    
    @staticmethod
    def get_activities_by_infrastructure(infrastructure_id):
        """Get all activities using this infrastructure"""
        infrastructure = Infrastructure.objects.get(pk=infrastructure_id)
        return infrastructure.activites.all()
    
    @staticmethod
    def get_available_infrastructures(date_debut, duree):
        """Get infrastructures available for a specific time slot"""
        # Get all available infrastructures
        infrastructures = Infrastructure.objects.filter(disponible=True)
        
        # Calculate end time
        from django.utils import timezone
        date_fin = date_debut + timezone.timedelta(minutes=duree)
        
        # Get IDs of infrastructures already booked during this time
        occupied_ids = Activite.objects.filter(
            infrastructure__isnull=False,
            date_debut__lt=date_fin,
            date_fin__gt=date_debut
        ).values_list('infrastructure_id', flat=True)
        
        # Exclude occupied infrastructures
        return infrastructures.exclude(id__in=occupied_ids)