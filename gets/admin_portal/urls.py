# admin_portal/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView

# Import views for each section
from admin_portal.views.dashboard_views import DashboardView
from admin_portal.views.participant_views import (
    ParticipantListView, ParticipantDetailView, ParticipantCreateView,
    ParticipantUpdateView, ParticipantDeleteView, participant_search
)
from admin_portal.views.activite_views import (
    ActiviteListView, ActiviteDetailView, ActiviteCreateView,
    ActiviteUpdateView, ActiviteDeleteView, activite_search,
    CalendrierActivitesView
)
from admin_portal.views.inscription_views import (
    InscriptionCreateView, InscriptionUpdateView, InscriptionDeleteView
)
from admin_portal.views.responsable_views import (
    ResponsableListView, ResponsableDetailView, ResponsableCreateView,
    ResponsableUpdateView, ResponsableDeleteView, responsable_search
)
from admin_portal.views.animateur_views import (
    AnimateurListView, AnimateurDetailView, AnimateurCreateView,
    AnimateurUpdateView, AnimateurDeleteView, animateur_search
)
from admin_portal.views.infrastructure_views import (
    InfrastructureListView, InfrastructureDetailView, InfrastructureCreateView,
    InfrastructureUpdateView, InfrastructureDeleteView, infrastructure_search
)
from admin_portal.views.materiel_views import (
    MaterielListView, MaterielDetailView, MaterielCreateView,
    MaterielUpdateView, MaterielDeleteView, materiel_search
)
from admin_portal.views.search_views import RecherceAdvancedView
from admin_portal.views.auth_views import (
    AdminLoginView, ProfileView, PasswordChangeView
)

app_name = 'admin_portal'

urlpatterns = [
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Authentication
    path('login/', AdminLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='admin_portal:login'), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/change-password/', PasswordChangeView.as_view(), name='change_password'),
    
    # Participants
    path('participants/', ParticipantListView.as_view(), name='participant_list'),
    path('participants/search/', participant_search, name='participant_search'),
    path('participants/create/', ParticipantCreateView.as_view(), name='participant_create'),
    path('participants/<int:pk>/', ParticipantDetailView.as_view(), name='participant_detail'),
    path('participants/<int:pk>/edit/', ParticipantUpdateView.as_view(), name='participant_edit'),
    path('participants/<int:pk>/delete/', ParticipantDeleteView.as_view(), name='participant_delete'),
    
    # Activités
    path('activites/', ActiviteListView.as_view(), name='activite_list'),
    path('activites/search/', activite_search, name='activite_search'),
    path('activites/create/', ActiviteCreateView.as_view(), name='activite_create'),
    path('activites/<int:pk>/', ActiviteDetailView.as_view(), name='activite_detail'),
    path('activites/<int:pk>/edit/', ActiviteUpdateView.as_view(), name='activite_edit'),
    path('activites/<int:pk>/delete/', ActiviteDeleteView.as_view(), name='activite_delete'),
    path('activites/calendrier/', CalendrierActivitesView.as_view(), name='calendrier_activites'),
    
    # Inscriptions
    path('inscriptions/create/', InscriptionCreateView.as_view(), name='inscription_create'),
    path('inscriptions/<int:pk>/edit/', InscriptionUpdateView.as_view(), name='inscription_edit'),
    path('inscriptions/<int:pk>/delete/', InscriptionDeleteView.as_view(), name='inscription_delete'),
    
    # Responsables
    path('responsables/', ResponsableListView.as_view(), name='responsable_list'),
    path('responsables/search/', responsable_search, name='responsable_search'),
    path('responsables/create/', ResponsableCreateView.as_view(), name='responsable_create'),
    path('responsables/<int:pk>/', ResponsableDetailView.as_view(), name='responsable_detail'),
    path('responsables/<int:pk>/edit/', ResponsableUpdateView.as_view(), name='responsable_edit'),
    path('responsables/<int:pk>/delete/', ResponsableDeleteView.as_view(), name='responsable_delete'),
    
    # Animateurs
    path('animateurs/', AnimateurListView.as_view(), name='animateur_list'),
    path('animateurs/search/', animateur_search, name='animateur_search'),
    path('animateurs/create/', AnimateurCreateView.as_view(), name='animateur_create'),
    path('animateurs/<int:pk>/', AnimateurDetailView.as_view(), name='animateur_detail'),
    path('animateurs/<int:pk>/edit/', AnimateurUpdateView.as_view(), name='animateur_edit'),
    path('animateurs/<int:pk>/delete/', AnimateurDeleteView.as_view(), name='animateur_delete'),
    
    # Infrastructures
    path('infrastructures/', InfrastructureListView.as_view(), name='infrastructure_list'),
    path('infrastructures/search/', infrastructure_search, name='infrastructure_search'),
    path('infrastructures/create/', InfrastructureCreateView.as_view(), name='infrastructure_create'),
    path('infrastructures/<int:pk>/', InfrastructureDetailView.as_view(), name='infrastructure_detail'),
    path('infrastructures/<int:pk>/edit/', InfrastructureUpdateView.as_view(), name='infrastructure_edit'),
    path('infrastructures/<int:pk>/delete/', InfrastructureDeleteView.as_view(), name='infrastructure_delete'),
    
    # Matériel
    path('materiel/', MaterielListView.as_view(), name='materiel_list'),
    path('materiel/search/', materiel_search, name='materiel_search'),
    path('materiel/create/', MaterielCreateView.as_view(), name='materiel_create'),
    path('materiel/<int:pk>/', MaterielDetailView.as_view(), name='materiel_detail'),
    path('materiel/<int:pk>/edit/', MaterielUpdateView.as_view(), name='materiel_edit'),
    path('materiel/<int:pk>/delete/', MaterielDeleteView.as_view(), name='materiel_delete'),
    
    # Recherche
    path('recherche/', RecherceAdvancedView.as_view(), name='recherche_avancee'),
]