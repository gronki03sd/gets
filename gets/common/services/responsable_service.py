# common/services/responsable_service.py
from django.db.models import Q
from common.models import Responsable

class ResponsableService:
    @staticmethod
    def get_all_responsables():
        return Responsable.objects.all()
    
    @staticmethod
    def get_responsable_by_id(responsable_id):
        try:
            return Responsable.objects.get(pk=responsable_id)
        except Responsable.DoesNotExist:
            return None
    
    @staticmethod
    def search_responsables(query=None):
        if not query:
            return Responsable.objects.all()
        
        return Responsable.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(email__icontains=query)
        )
    
    @staticmethod
    def create_responsable(form_data, user):
        responsable = form_data.save(commit=False)
        responsable.created_by = user
        responsable.save()
        return responsable
    
    @staticmethod
    def update_responsable(responsable_id, form_data):
        responsable = form_data.save()
        return responsable
    
    @staticmethod
    def delete_responsable(responsable_id):
        responsable = Responsable.objects.get(pk=responsable_id)
        responsable.delete()
        return True