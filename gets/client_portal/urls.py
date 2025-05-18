# client_portal/urls.py
from django.urls import path
from client_portal.views import (
    home_views, event_views, account_views, auth_views
)

app_name = 'client_portal'

urlpatterns = [
    # Home and Basic Pages
    path('', home_views.HomeView.as_view(), name='home'),
    path('about/', home_views.AboutView.as_view(), name='about'),
    path('contact/', home_views.ContactView.as_view(), name='contact'),
    
    # Authentication
    path('login/', auth_views.ClientLoginView.as_view(), name='login'),
    path('logout/', auth_views.ClientLogoutView.as_view(), name='logout'),
    path('register/', auth_views.ClientRegisterView.as_view(), name='register'),
    
    # Events
    path('events/', event_views.EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', event_views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/register/', event_views.EventRegisterView.as_view(), name='event_register'),
    
    # User Account
    path('account/dashboard/', account_views.DashboardView.as_view(), name='dashboard'),
    path('account/profile/', account_views.ProfileView.as_view(), name='profile'),
    path('account/participant-info/', account_views.ParticipantInfoView.as_view(), name='participant_info'),
    path('account/cancel-registration/<int:inscription_id>/', account_views.CancelRegistrationView.as_view(), name='cancel_registration'),
]