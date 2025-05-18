from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

from .models import (
    User, Participant, Activite, Inscription
)
from .forms import (
    UserRegisterForm, UserLoginForm, UserProfileForm, UserPasswordChangeForm,
    ParticipantForm, ClientInscriptionForm,
    # Add the missing imports
    ClientRegistrationForm, ClientLoginForm
)

# Client Home Page
def client_home(request):
    # Get upcoming activities for display on the homepage
    upcoming_activities = Activite.objects.filter(
        date_debut__gte=timezone.now()
    ).order_by('date_debut')[:6]  # Limit to 6 for display
    
    return render(request, 'client/home.html', {
        'upcoming_activities': upcoming_activities
    })

# Client Events List Page
def client_event_list(request):
    # Add search and filtering logic
    search_query = request.GET.get('search', '')
    date_filter = request.GET.get('date', '')
    
    activities = Activite.objects.filter(date_debut__gte=timezone.now())
    
    if search_query:
        activities = activities.filter(
            Q(nom__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if date_filter:
        try:
            filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            activities = activities.filter(date_debut__date=filter_date)
        except ValueError:
            # If date format is invalid, ignore the filter
            pass
    
    return render(request, 'client/events/list.html', {
        'activities': activities,
        'search_query': search_query,
        'date_filter': date_filter
    })

# Client Event Detail Page
def client_event_detail(request, pk):
    activity = get_object_or_404(Activite, pk=pk)
    
    # Check if the user can register (if logged in and has participant info)
    can_register = False
    user_already_registered = False
    
    if request.user.is_authenticated:
        # Check if user has participant information linked
        participant = None
        try:
            # Try to find a participant record that matches the user's information
            participant = Participant.objects.filter(
                email=request.user.email
            ).first()
            
            if participant:
                can_register = True
                # Check if already registered for this activity
                user_already_registered = Inscription.objects.filter(
                    participant=participant,
                    activite=activity
                ).exists()
        except:
            can_register = False
    
    return render(request, 'client/events/detail.html', {
        'activity': activity,
        'can_register': can_register,
        'user_already_registered': user_already_registered
    })

# Client Registration for Event
@login_required
def client_event_register(request, pk):
    activity = get_object_or_404(Activite, pk=pk)
    
    # Check if activity is full
    if activity.est_complete():
        messages.error(request, "Cette activité est complète. Impossible de s'inscrire.")
        return redirect('client_event_detail', pk=pk)
    
    # Find or create participant based on user info
    try:
        participant = Participant.objects.filter(email=request.user.email).first()
        
        if not participant:
            # Create participant based on user info
            participant = Participant(
                nom=request.user.last_name,
                prenom=request.user.first_name,
                email=request.user.email,
                telephone=request.user.phone_number,
                date_naissance=timezone.now().date() - timezone.timedelta(days=365*20),  # Default age
                created_by=request.user
            )
            participant.save()
        
        # Check if already registered
        if Inscription.objects.filter(participant=participant, activite=activity).exists():
            messages.warning(request, "Vous êtes déjà inscrit à cette activité.")
            return redirect('client_event_detail', pk=pk)
        
        # Create the registration
        inscription = Inscription(
            participant=participant,
            activite=activity,
            statut='inscrit',
            created_by=request.user
        )
        inscription.save()
        
        messages.success(request, f"Vous êtes inscrit avec succès à l'activité: {activity.nom}")
        return redirect('client_dashboard')
    
    except Exception as e:
        messages.error(request, f"Une erreur s'est produite lors de l'inscription: {str(e)}")
        return redirect('client_event_detail', pk=pk)

@login_required
def client_dashboard(request):
    # Try to find participant based on user email
    participant = None
    inscriptions = []
    
    try:
        participant = Participant.objects.filter(email=request.user.email).first()
        if participant:
            inscriptions = Inscription.objects.filter(participant=participant)
    except:
        pass
    
    # Get upcoming activities
    upcoming_activities = Activite.objects.filter(
        date_debut__gte=timezone.now()
    ).order_by('date_debut')[:4]  # Limit to 4 for display
    
    return render(request, 'client/account/dashboard.html', {
        'participant': participant,
        'inscriptions': inscriptions,
        'upcoming_activities': upcoming_activities
    })

# Client Profile
@login_required
def client_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            
            # Update participant info if exists
            participant = Participant.objects.filter(email=request.user.email).first()
            if participant:
                participant.nom = request.user.last_name
                participant.prenom = request.user.first_name
                participant.email = request.user.email
                participant.telephone = request.user.phone_number
                participant.save()
            
            messages.success(request, "Votre profil a été mis à jour.")
            return redirect('client_profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Check if the user has a participant record
    has_participant = Participant.objects.filter(email=request.user.email).exists()
    
    return render(request, 'client/account/profile.html', {
        'form': form,
        'has_participant': has_participant
    })

# Client Update Participant Info
@login_required
def client_update_participant(request):
    # Find existing participant or prepare to create new one
    participant = Participant.objects.filter(email=request.user.email).first()
    
    if request.method == 'POST':
        form = ParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            participant = form.save(commit=False)
            
            # Link to the current user
            if not participant.email:
                participant.email = request.user.email
            if not participant.created_by:
                participant.created_by = request.user
                
            participant.save()
            messages.success(request, "Vos informations de participant ont été mises à jour.")
            return redirect('client_profile')
    else:
        # Pre-fill with user info if creating new participant
        initial_data = {}
        if not participant:
            initial_data = {
                'nom': request.user.last_name,
                'prenom': request.user.first_name,
                'email': request.user.email,
                'telephone': request.user.phone_number
            }
        form = ParticipantForm(instance=participant, initial=initial_data)
    
    return render(request, 'client/account/participant_form.html', {
        'form': form,
        'is_new': participant is None
    })

# Cancel Registration
@login_required
def client_cancel_registration(request, inscription_id):
    inscription = get_object_or_404(Inscription, id=inscription_id)
    
    # Security check - make sure the logged in user owns this registration
    participant = Participant.objects.filter(email=request.user.email).first()
    if not participant or inscription.participant != participant:
        messages.error(request, "Vous n'êtes pas autorisé à annuler cette inscription.")
        return redirect('client_dashboard')
    
    if request.method == 'POST':
        inscription.statut = 'annule'
        inscription.save()
        messages.success(request, f"Votre inscription à {inscription.activite.nom} a été annulée.")
        return redirect('client_dashboard')
    
    return render(request, 'client/booking/cancel.html', {
        'inscription': inscription
    })


def client_register(request):
    """Client-side user registration"""
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Votre compte a été créé avec succès! Vous pouvez maintenant vous connecter.")
            return redirect('client_login')
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'client/register.html', {'form': form})

def client_login(request):
    """Client login page"""
    if request.method == 'POST':
        form = ClientLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue, {user.first_name or user.username}!")
                return redirect('client_dashboard')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = ClientLoginForm()
    
    return render(request, 'client/login.html', {'form': form})