# common/services/participant_service.py
from django.db.models import Q
from common.models import Participant

class ParticipantService:
    @staticmethod
    def get_all_participants():
        return Participant.objects.all()
    
    @staticmethod
    def get_participant_by_id(participant_id):
        try:
            return Participant.objects.get(pk=participant_id)
        except Participant.DoesNotExist:
            return None
    
    @staticmethod
    def search_participants(query=None):
        if not query:
            return Participant.objects.all()
        
        return Participant.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(email__icontains=query)
        )
    
    @staticmethod
    def create_participant(form_data, user):
        participant = form_data.save(commit=False)
        participant.created_by = user
        participant.save()
        return participant
    
    @staticmethod
    def update_participant(participant_id, form_data):
        participant = form_data.save()
        return participant
    
    @staticmethod
    def delete_participant(participant_id):
        participant = Participant.objects.get(pk=participant_id)
        participant.delete()
        return True