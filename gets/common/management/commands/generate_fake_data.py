import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from common.models import User, Participant, Responsable, Animateur, Infrastructure, Materiel, Activite, Inscription

class Command(BaseCommand):
    help = 'Generate fake data for testing the GETS system'

    def add_arguments(self, parser):
        parser.add_argument('--participants', type=int, default=50, help='Number of participants to create')
        parser.add_argument('--responsables', type=int, default=10, help='Number of responsables to create')
        parser.add_argument('--animateurs', type=int, default=20, help='Number of animateurs to create')
        parser.add_argument('--infrastructures', type=int, default=15, help='Number of infrastructures to create')
        parser.add_argument('--materiels', type=int, default=25, help='Number of materiels to create')
        parser.add_argument('--activites', type=int, default=30, help='Number of activites to create')
        parser.add_argument('--inscriptions', type=int, default=100, help='Number of inscriptions to create')

    def handle(self, *args, **options):
        fake = Faker(['fr_FR'])
        admin_user = self._get_or_create_admin()
        
        self.stdout.write('Generating fake data...')
        
        # Create participants
        participants = []
        self.stdout.write('Creating participants...')
        for _ in range(options['participants']):
            participant = Participant.objects.create(
                nom=fake.last_name(),
                prenom=fake.first_name(),
                date_naissance=fake.date_of_birth(minimum_age=5, maximum_age=80),
                adresse=fake.address(),
                telephone=fake.phone_number(),
                email=fake.email(),
                created_by=admin_user
            )
            participants.append(participant)
            self.stdout.write(f'Created participant: {participant}')
            
        # Create responsables
        responsables = []
        self.stdout.write('Creating responsables...')
        for _ in range(options['responsables']):
            responsable = Responsable.objects.create(
                nom=fake.last_name(),
                prenom=fake.first_name(),
                specialite=random.choice(['Sport', 'Arts', 'Sciences', 'Musique', 'Cuisine', 'Jeux', 'Langues']),
                telephone=fake.phone_number(),
                email=fake.email(),
                created_by=admin_user
            )
            responsables.append(responsable)
            self.stdout.write(f'Created responsable: {responsable}')
            
        # Create animateurs
        animateurs = []
        self.stdout.write('Creating animateurs...')
        for _ in range(options['animateurs']):
            animateur = Animateur.objects.create(
                nom=fake.last_name(),
                prenom=fake.first_name(),
                competence=random.choice(['Animation', 'Coaching', 'Enseignement', 'Arts', 'Jeux', 'Sport', 'Musique']),
                telephone=fake.phone_number(),
                email=fake.email(),
                created_by=admin_user
            )
            animateurs.append(animateur)
            self.stdout.write(f'Created animateur: {animateur}')
            
        # Create infrastructures
        infrastructures = []
        self.stdout.write('Creating infrastructures...')
        types = ['Salle', 'Terrain', 'Gymnase', 'Piscine', 'Salle de spectacle', 'Salle de conférence', 'Terrain sportif']
        for _ in range(options['infrastructures']):
            infrastructure = Infrastructure.objects.create(
                nom=f"{random.choice(types)} {fake.city()}",
                type=random.choice(types),
                capacite=random.randint(10, 300),
                localisation=fake.address(),
                disponible=random.choice([True, True, True, False]),  # 75% disponible
                created_by=admin_user
            )
            infrastructures.append(infrastructure)
            self.stdout.write(f'Created infrastructure: {infrastructure}')
            
        # Create materiels
        materiels = []
        self.stdout.write('Creating materiels...')
        mat_types = ['Ballons', 'Tables', 'Chaises', 'Équipement sportif', 'Équipement son', 'Matériel informatique', 'Jeux']
        for _ in range(options['materiels']):
            materiel = Materiel.objects.create(
                nom=f"{random.choice(mat_types)} - {fake.word()}",
                description=fake.text(max_nb_chars=200),
                quantite_disponible=random.randint(1, 50),
                created_by=admin_user
            )
            materiels.append(materiel)
            self.stdout.write(f'Created materiel: {materiel}')
            
        # Create activites
        activites = []
        self.stdout.write('Creating activites...')
        activity_names = ['Cours de', 'Atelier de', 'Séance de', 'Journée', 'Initiation à', 'Formation', 'Découverte de']
        activities = ['Natation', 'Football', 'Tennis', 'Danse', 'Théâtre', 'Musique', 'Peinture', 'Cuisine', 'Yoga', 'Jeux de société']
        
        now = timezone.now()
        
        for _ in range(options['activites']):
            # 70% future events, 30% past events
            if random.random() < 0.7:
                date_debut = now + timedelta(days=random.randint(1, 180))
            else:
                date_debut = now - timedelta(days=random.randint(1, 180))
                
            activite = Activite.objects.create(
                nom=f"{random.choice(activity_names)} {random.choice(activities)}",
                description=fake.paragraph(nb_sentences=5),
                duree=random.choice([60, 90, 120, 180, 240, 300]),
                date_debut=date_debut,
                responsable=random.choice(responsables) if responsables else None,
                infrastructure=random.choice(infrastructures) if infrastructures else None,
                capacite_max=random.randint(10, 100),
                created_by=admin_user
            )
            
            # Add animateurs
            num_animateurs = random.randint(1, min(3, len(animateurs)))
            for animateur in random.sample(animateurs, num_animateurs):
                activite.animateurs.add(animateur)
                
            # Add materiels
            num_materiels = random.randint(1, min(5, len(materiels)))
            for materiel in random.sample(materiels, num_materiels):
                activite.activite_materiels.create(
                    materiel=materiel,
                    quantite_requise=random.randint(1, 5)
                )
                
            activites.append(activite)
            self.stdout.write(f'Created activite: {activite}')
            
        # Create inscriptions
        self.stdout.write('Creating inscriptions...')
        statuts = ['inscrit', 'en_attente', 'annule']
        weights = [0.7, 0.2, 0.1]  # 70% inscrit, 20% en attente, 10% annulé
        
        for _ in range(options['inscriptions']):
            if not participants or not activites:
                break
                
            participant = random.choice(participants)
            activite = random.choice(activites)
            
            # Check if already registered
            if Inscription.objects.filter(participant=participant, activite=activite).exists():
                continue
                
            statut = random.choices(statuts, weights=weights)[0]
            
            inscription = Inscription.objects.create(
                participant=participant,
                activite=activite,
                statut=statut,
                created_by=admin_user
            )
            self.stdout.write(f'Created inscription: {inscription}')
            
        self.stdout.write(self.style.SUCCESS('Successfully generated fake data!'))
    
    def _get_or_create_admin(self):
        try:
            return User.objects.get(username='admin')
        except User.DoesNotExist:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword',
                role='admin'
            )
            return admin