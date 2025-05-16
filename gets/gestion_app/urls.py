from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Participants
    path('participants/', views.participant_list, name='participant_list'),
    path('participants/search/', views.participant_search, name='participant_search'),
    path('participants/create/', views.participant_create, name='participant_create'),
    path('participants/<int:pk>/', views.participant_detail, name='participant_detail'),
    path('participants/<int:pk>/edit/', views.participant_edit, name='participant_edit'),
    path('participants/<int:pk>/delete/', views.participant_delete, name='participant_delete'),
    
    # Activités
    path('activites/', views.activite_list, name='activite_list'),
    path('activites/search/', views.activite_search, name='activite_search'),
    path('activites/create/', views.activite_create, name='activite_create'),
    path('activites/<int:pk>/', views.activite_detail, name='activite_detail'),
    path('activites/<int:pk>/edit/', views.activite_edit, name='activite_edit'),
    path('activites/<int:pk>/delete/', views.activite_delete, name='activite_delete'),
    path('activites/calendrier/', views.calendrier_activites, name='calendrier_activites'),
    
    # Inscriptions
    path('inscriptions/create/', views.inscription_create, name='inscription_create'),
    path('inscriptions/<int:pk>/edit/', views.inscription_edit, name='inscription_edit'),
    path('inscriptions/<int:pk>/delete/', views.inscription_delete, name='inscription_delete'),
    
    # Responsables
    path('responsables/', views.responsable_list, name='responsable_list'),
    path('responsables/create/', views.responsable_create, name='responsable_create'),
    path('responsables/<int:pk>/', views.responsable_detail, name='responsable_detail'),
    path('responsables/<int:pk>/edit/', views.responsable_edit, name='responsable_edit'),
    path('responsables/<int:pk>/delete/', views.responsable_delete, name='responsable_delete'),
    
    # Animateurs
    path('animateurs/', views.animateur_list, name='animateur_list'),
    path('animateurs/create/', views.animateur_create, name='animateur_create'),
    path('animateurs/<int:pk>/', views.animateur_detail, name='animateur_detail'),
    path('animateurs/<int:pk>/edit/', views.animateur_edit, name='animateur_edit'),
    path('animateurs/<int:pk>/delete/', views.animateur_delete, name='animateur_delete'),
    
    # Infrastructures
    path('infrastructures/', views.infrastructure_list, name='infrastructure_list'),
    path('infrastructures/create/', views.infrastructure_create, name='infrastructure_create'),
    path('infrastructures/<int:pk>/', views.infrastructure_detail, name='infrastructure_detail'),
    path('infrastructures/<int:pk>/edit/', views.infrastructure_edit, name='infrastructure_edit'),
    path('infrastructures/<int:pk>/delete/', views.infrastructure_delete, name='infrastructure_delete'),
    
    # Matériel
    path('materiel/', views.materiel_list, name='materiel_list'),
    path('materiel/create/', views.materiel_create, name='materiel_create'),
    path('materiel/<int:pk>/', views.materiel_detail, name='materiel_detail'),
    path('materiel/<int:pk>/edit/', views.materiel_edit, name='materiel_edit'),
    path('materiel/<int:pk>/delete/', views.materiel_delete, name='materiel_delete'),
    
    # Recherche
    path('recherche/', views.recherche_avancee, name='recherche_avancee'),
]

