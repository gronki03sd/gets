# common/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone

class User(AbstractUser):
    """
    Custom user model for the event management system
    """
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('manager', 'Gestionnaire'),
        ('staff', 'Personnel'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    class Meta:
        db_table = 'user'
    
    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_manager(self):
        return self.role == 'manager' or self.role == 'admin'


class Participant(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    adresse = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    date_inscription = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_participants')
    
    class Meta:
        db_table = 'participant'
        
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    def get_activites(self):
        return [inscription.activite for inscription in self.inscription_set.all()]
    
    def est_inscrit(self, activite):
        return self.inscriptions.filter(activite=activite).exists()


class Responsable(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_responsables')
    
    class Meta:
        db_table = 'responsable'
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Animateur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    competence = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_animateurs')
    
    class Meta:
        db_table = 'animateur'
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Infrastructure(models.Model):
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    capacite = models.IntegerField(blank=True, null=True)
    localisation = models.CharField(max_length=100, blank=True, null=True)
    disponible = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_infrastructures')
    
    class Meta:
        db_table = 'infrastructure'
    
    def __str__(self):
        return self.nom


class Materiel(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    quantite_disponible = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_materiels')
    
    class Meta:
        db_table = 'materiel'
    
    def __str__(self):
        return self.nom


class Activite(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    duree = models.IntegerField(help_text="Durée en minutes")
    date_debut = models.DateTimeField()
    responsable = models.ForeignKey('Responsable', on_delete=models.SET_NULL, blank=True, null=True, related_name='activites')
    infrastructure = models.ForeignKey('Infrastructure', on_delete=models.SET_NULL, blank=True, null=True, related_name='activites')
    capacite_max = models.IntegerField(blank=True, null=True)
    animateurs = models.ManyToManyField('Animateur', through='ActiviteAnimateur', related_name='activites')
    materiels = models.ManyToManyField('Materiel', through='ActiviteMateriel', related_name='activites')
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_activites')
    
    class Meta:
        db_table = 'activite'
    
    def __str__(self):
        return self.nom
    
    def get_participants(self):
        return [inscription.participant for inscription in self.inscriptions.all()]
    
    def nombre_places_restantes(self):
        if not self.capacite_max:
            return None
        places_prises = self.inscriptions.count()
        return max(0, self.capacite_max - places_prises)
    
    def est_complete(self):
        if not self.capacite_max:
            return False
        return self.nombre_places_restantes() <= 0
    
    # Méthodes supplémentaires pour le calendrier
    def get_absolute_url(self):
        return reverse('admin_portal:activite_detail', args=[str(self.id)])
    
    @property
    def get_html_url(self):
        """Renvoie l'événement formaté avec un lien HTML pour l'affichage dans le calendrier"""
        url = reverse('admin_portal:activite_detail', args=[str(self.id)])
        debut = self.get_heure_debut()
        fin = self.get_heure_fin()
        return f'<li class="calendar-event" data-id="{self.id}">{self.nom} ({debut}-{fin})</li>'
    
    def get_heure_debut(self):
        return self.date_debut.strftime('%H:%M')
    
    def get_heure_fin(self):
        # Calculer la date de fin en ajoutant la durée
        date_fin = self.date_debut + timezone.timedelta(minutes=self.duree)
        return date_fin.strftime('%H:%M')
    
    @property
    def date_fin(self):
        """Calcule la date de fin en fonction de la date de début et de la durée"""
        return self.date_debut + timezone.timedelta(minutes=self.duree)
    
    @property
    def est_a_venir(self):
        return self.date_debut > timezone.now()


class ActiviteAnimateur(models.Model):
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name='activite_animateurs')
    animateur = models.ForeignKey(Animateur, on_delete=models.CASCADE, related_name='activite_animateurs')
    
    class Meta:
        db_table = 'activite_animateur'
        unique_together = ('activite', 'animateur')
    
    def __str__(self):
        return f"{self.activite} - {self.animateur}"


class ActiviteMateriel(models.Model):
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name='activite_materiels')
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE, related_name='activite_materiels')
    quantite_requise = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'activite_materiel'
        unique_together = ('activite', 'materiel')
    
    def __str__(self):
        return f"{self.activite} - {self.materiel} ({self.quantite_requise})"


class Inscription(models.Model):
    STATUT_CHOICES = [
        ('inscrit', 'Inscrit'),
        ('en_attente', 'En attente'),
        ('annule', 'Annulé'),
    ]
    
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='inscriptions')
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name='inscriptions')
    date_inscription = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='inscrit')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_inscriptions')
    
    class Meta:
        db_table = 'inscription'
        unique_together = ('participant', 'activite')
    
    def __str__(self):
        return f"{self.participant} - {self.activite}"