# common/services/inscription_service.py
from django.utils import timezone
from common.models import Inscription, Participant, Activite

class InscriptionService:
    @staticmethod
    def get_all_inscriptions():
        return Inscription.objects.all()
    
    @staticmethod
    def get_inscription_by_id(inscription_id):
        try:
            return Inscription.objects.get(pk=inscription_id)
        except Inscription.DoesNotExist:
            return None
    
    @staticmethod
    def create_inscription(participant_id, activite_id, statut, user):
        # Business logic for validating registration
        participant = Participant.objects.get(pk=participant_id)
        activite = Activite.objects.get(pk=activite_id)
        
        # Check if activity is full
        if activite.est_complete():
            raise ValueError("Cette activité est complète. Impossible de s'inscrire.")
        
        # Check if already registered
        if Inscription.objects.filter(participant=participant, activite=activite).exists():
            raise ValueError(f"{participant} est déjà inscrit à cette activité.")
        
        inscription = Inscription(
            participant=participant,
            activite=activite,
            statut=statut,
            created_by=user
        )
        inscription.save()
        return inscription
    
    @staticmethod
    def update_inscription_status(inscription_id, new_status):
        inscription = Inscription.objects.get(pk=inscription_id)
        inscription.statut = new_status
        inscription.save()
        return inscription
    
    @staticmethod
    def cancel_inscription(inscription_id):
        return InscriptionService.update_inscription_status(inscription_id, 'annule')
    
    @staticmethod
    def delete_inscription(inscription_id):
        inscription = Inscription.objects.get(pk=inscription_id)
        inscription.delete()
        return True
    
    @staticmethod
    def get_inscriptions_by_participant(participant_id):
        return Inscription.objects.filter(participant_id=participant_id)
    
    @staticmethod
    def get_inscriptions_by_activite(activite_id):
        return Inscription.objects.filter(activite_id=activite_id)
    
    @staticmethod
    def client_register_for_event(user, activite_id):
        activite = Activite.objects.get(pk=activite_id)
        
        # Check if activity is full
        if activite.est_complete():
            raise ValueError("Cette activité est complète. Impossible de s'inscrire.")
        
        # Find or create participant based on user info
        participant = Participant.objects.filter(email=user.email).first()
        
        if not participant:
            # Create participant based on user info
            participant = Participant(
                nom=user.last_name,
                prenom=user.first_name,
                email=user.email,
                telephone=user.phone_number,
                date_naissance=timezone.now().date() - timezone.timedelta(days=365*20),  # Default age
                created_by=user
            )
            participant.save()
        
        # Check if already registered
        if Inscription.objects.filter(participant=participant, activite=activite).exists():
            raise ValueError("Vous êtes déjà inscrit à cette activité.")
        
        # Create the registration
        inscription = Inscription(
            participant=participant,
            activite=activite,
            statut='inscrit',
            created_by=user
        )
        inscription.save()
        
        return inscription