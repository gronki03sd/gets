from datetime import datetime, timedelta, date
from io import BytesIO
import calendar

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.db.models import Q, Count
from django.utils import timezone 
from django.utils.safestring import mark_safe

from .models import (
    User, Participant, Activite, Responsable, Animateur, 
    Infrastructure, Materiel, Inscription, ActiviteAnimateur, ActiviteMateriel
)
from .forms import (
    UserRegisterForm, UserLoginForm, UserProfileForm, UserPasswordChangeForm,
    ParticipantForm, ActiviteForm, InscriptionForm, ActiviteSearchForm,
    ResponsableForm, AnimateurForm, InfrastructureForm, MaterielForm , ActiviteForm, ActiviteMaterielForm, ActiviteAnimateurForm # Nouveaux formulaires
)

# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Compte créé pour {username}. Vous pouvez maintenant vous connecter.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'auth/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Utilisation directe des valeurs soumises
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenue, {username}!")
            
            # Redirection forcée avec l'URL complète
            return redirect('/')  # URL absolue vers la racine (dashboard)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
    
    # Si GET ou si l'authentification a échoué
    form = UserLoginForm()
    return render(request, 'auth/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect('login')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'auth/profile.html', {'form': form})

# Dashboard
@login_required
def dashboard(request):
    # Statistiques de base
    total_participants = Participant.objects.count()
    total_activites = Activite.objects.count()
    total_inscriptions = Inscription.objects.count()
    
    # Activités à venir
    activites_a_venir = Activite.objects.filter(
        date_debut__gte=timezone.now()
    ).order_by('date_debut')[:5]
    
    # Activités populaires (par nombre d'inscriptions)
    from django.db.models import Count
    activites_populaires = Activite.objects.annotate(
        nombre_inscrits=Count('inscriptions')
    ).order_by('-nombre_inscrits')[:5]
    
    # Derniers participants inscrits
    recent_participants = Participant.objects.order_by('-date_inscription')[:5]
    
    # Statistiques par jour (pour graphique)
    from django.db.models.functions import TruncDate
    inscriptions_par_jour = Inscription.objects.annotate(
        date=TruncDate('date_inscription')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')[:14]  # 2 dernières semaines
    
    context = {
        'total_participants': total_participants,
        'total_activites': total_activites,
        'total_inscriptions': total_inscriptions,
        'activites_a_venir': activites_a_venir,
        'activites_populaires': activites_populaires,
        'recent_participants': recent_participants,
        'inscriptions_par_jour': list(inscriptions_par_jour),
    }
    return render(request, 'dashboard/index.html', context)

# Participant Views
@login_required
def participant_list(request):
    participants = Participant.objects.all()
    return render(request, 'participants/list.html', {'participants': participants})

@login_required
def participant_search(request):
    search_query = request.GET.get('q', '')
    if search_query:
        participants = Participant.objects.filter(
            Q(nom__icontains=search_query) | 
            Q(prenom__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    else:
        participants = Participant.objects.all()
    
    return render(request, 'partials/participant_list.html', {'participants': participants})

@login_required
def participant_detail(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    inscriptions = participant.inscriptions.all()
    return render(request, 'participants/detail.html', {'participant': participant, 'inscriptions': inscriptions})

@login_required
def participant_create(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.created_by = request.user
            participant.save()
            messages.success(request, f"Participant {participant} ajouté avec succès!")
            
            # Si c'est une requête HTMX, renvoyer la liste mise à jour
            if request.headers.get('HX-Request'):
                participants = Participant.objects.all()
                return render(request, 'partials/participant_list.html', {'participants': participants})
            else:
                return redirect('participant_list')
    else:
        form = ParticipantForm()
    
    # Si c'est une requête HTMX, renvoyer seulement le formulaire
    if request.headers.get('HX-Request'):
        return render(request, 'partials/participant_form.html', {'form': form})
    
    return render(request, 'participants/create.html', {'form': form})

@login_required
def participant_edit(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        form = ParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, f"Participant {participant} modifié avec succès!")
            return redirect('participant_detail', pk=participant.pk)
    else:
        form = ParticipantForm(instance=participant)
    
    return render(request, 'participants/edit.html', {'form': form, 'participant': participant})

@login_required
def participant_delete(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        nom = participant.nom
        participant.delete()
        messages.success(request, f"Participant {nom} supprimé avec succès!")
        return redirect('participant_list')
    
    return render(request, 'participants/delete.html', {'participant': participant})

# Activité Views
@login_required
def activite_list(request):
    form = ActiviteSearchForm()
    activites = Activite.objects.all()
    return render(request, 'activites/list.html', {'activites': activites, 'form': form})

@login_required
def activite_search(request):
    form = ActiviteSearchForm(request.GET)
    activites = Activite.objects.all()
    
    date_debut = request.GET.get('date_debut')
    nom = request.GET.get('nom')
    
    if date_debut:
        activites = activites.filter(date_debut__date=date_debut)
    if nom:
        activites = activites.filter(nom__icontains=nom)
    
    return render(request, 'partials/activite_list.html', {'activites': activites})

@login_required
def activite_detail(request, pk):
    activite = get_object_or_404(Activite, pk=pk)
    inscriptions = activite.inscriptions.all()
    materiels = activite.activite_materiels.all()
    return render(request, 'activites/detail.html', {
        'activite': activite, 
        'inscriptions': inscriptions,
        'materiels': materiels
    })

@login_required
def activite_create(request):
    if request.method == 'POST':
        form = ActiviteForm(request.POST)
        if form.is_valid():
            activite = form.save(commit=False)
            activite.created_by = request.user
            activite.save()
            messages.success(request, f"Activité {activite} créée avec succès!")
            return redirect('activite_list')
    else:
        form = ActiviteForm()
    
    return render(request, 'activites/create.html', {'form': form})

@login_required
def activite_edit(request, pk):
    activite = get_object_or_404(Activite, pk=pk)
    if request.method == 'POST':
        form = ActiviteForm(request.POST, instance=activite)
        if form.is_valid():
            form.save()
            messages.success(request, f"Activité {activite} modifiée avec succès!")
            return redirect('activite_detail', pk=activite.pk)
    else:
        form = ActiviteForm(instance=activite)
    
    return render(request, 'activites/edit.html', {'form': form, 'activite': activite})

@login_required
def activite_delete(request, pk):
    activite = get_object_or_404(Activite, pk=pk)
    if request.method == 'POST':
        nom = activite.nom
        activite.delete()
        messages.success(request, f"Activité {nom} supprimée avec succès!")
        return redirect('activite_list')
    
    return render(request, 'activites/delete.html', {'activite': activite})

# Inscription Views
@login_required
def inscription_create(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            activite = form.cleaned_data['activite']
            participant = form.cleaned_data['participant']
            
            # Vérifier si l'activité est complète
            if activite.est_complete():
                messages.error(request, f"L'activité {activite} est complète!")
                return redirect('activite_detail', pk=activite.pk)
            
            # Vérifier si le participant est déjà inscrit
            if participant.est_inscrit(activite):
                messages.error(request, f"{participant} est déjà inscrit à cette activité!")
                return redirect('activite_detail', pk=activite.pk)
            
            inscription = form.save(commit=False)
            inscription.created_by = request.user
            inscription.save()
            
            messages.success(request, f"Inscription de {participant} à {activite} réussie!")
            
            # Si la requête provient de la page d'activité, rediriger vers cette activité
            if 'activite_id' in request.POST:
                return redirect('activite_detail', pk=request.POST['activite_id'])
            # Sinon, rediriger vers les détails du participant
            else:
                return redirect('participant_detail', pk=participant.pk)
    else:
        # Pré-remplir avec l'activité ou le participant si fourni dans l'URL
        initial = {}
        if 'activite_id' in request.GET:
            initial['activite'] = request.GET['activite_id']
        if 'participant_id' in request.GET:
            initial['participant'] = request.GET['participant_id']
        
        form = InscriptionForm(initial=initial)
    
    return render(request, 'inscriptions/create.html', {'form': form})

@login_required
def inscription_edit(request, pk):
    inscription = get_object_or_404(Inscription, pk=pk)
    if request.method == 'POST':
        form = InscriptionForm(request.POST, instance=inscription)
        if form.is_valid():
            form.save()
            messages.success(request, "Inscription modifiée avec succès!")
            return redirect('activite_detail', pk=inscription.activite.pk)
    else:
        form = InscriptionForm(instance=inscription)
    
    return render(request, 'inscriptions/edit.html', {'form': form, 'inscription': inscription})

@login_required
def inscription_delete(request, pk):
    inscription = get_object_or_404(Inscription, pk=pk)
    if request.method == 'POST':
        activite_pk = inscription.activite.pk
        participant_name = inscription.participant.prenom + " " + inscription.participant.nom
        activite_name = inscription.activite.nom
        inscription.delete()
        messages.success(request, f"Inscription de {participant_name} à {activite_name} supprimée!")
        
        # Rediriger vers la page d'où la suppression a été demandée
        referer = request.META.get('HTTP_REFERER')
        if referer and 'participant' in referer:
            return redirect('participant_detail', pk=inscription.participant.pk)
        else:
            return redirect('activite_detail', pk=activite_pk)
    
    return render(request, 'inscriptions/delete.html', {'inscription': inscription})



@login_required
def recherche_avancee(request):
    query = request.GET.get('q', '')
    type_recherche = request.GET.get('type', 'all')
    
    participants = []
    activites = []
    
    if query:
        if type_recherche in ['all', 'participants']:
            participants = Participant.objects.filter(
                Q(nom__icontains=query) | 
                Q(prenom__icontains=query) |
                Q(email__icontains=query) |
                Q(telephone__icontains=query)
            )
        
        if type_recherche in ['all', 'activites']:
            activites = Activite.objects.filter(
                Q(nom__icontains=query) | 
                Q(description__icontains=query)
            )
    
    context = {
        'query': query,
        'type_recherche': type_recherche,
        'participants': participants,
        'activites': activites,
    }
    
    return render(request, 'recherche/resultats.html', context)



from datetime import datetime, timedelta, date
from django.shortcuts import render
from django.utils.safestring import mark_safe
import calendar
from django.contrib.auth.decorators import login_required
from .models import Activite

class Calendar:
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        self.cal = calendar.monthcalendar(year, month)

    def formatday(self, day, activites, weekday):
        activites_per_day = activites.filter(date_debut__day=day)
        d = ''
        for activite in activites_per_day:
            d += f'<li class="calendar-event" data-id="{activite.id}">{activite.date_debut.strftime("%H:%M")} - {activite.nom}</li>'
        
        if day != 0:
            has_events = 'has-events' if activites_per_day else ''
            today_class = 'today' if date.today() == date(self.year, self.month, day) else ''
            weekend_class = 'weekend' if weekday >= 5 else ''
            return f"<td class='{has_events} {today_class} {weekend_class}'><span class='date'>{day}</span><ul class='calendar-events'>{d}</ul></td>"
        return '<td class="noday"></td>'

    def formatweek(self, theweek, activites):
        week = ''
        for i, day in enumerate(theweek):
            weekday = i  # 0 = lundi, 6 = dimanche dans notre représentation
            week += self.formatday(day, activites, weekday)
        return f'<tr>{week}</tr>'

    def formatmonth(self, withyear=True):
        activites = Activite.objects.filter(
            date_debut__year=self.year, 
            date_debut__month=self.month
        )
        
        cal = f'<table class="calendar table table-bordered">\n'
        cal += f'<thead><tr class="month-header"><th colspan="7">{calendar.month_name[self.month]} {self.year}</th></tr>\n'
        cal += f'<tr class="weekdays">'
        for day in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]:
            cal += f'<th class="header">{day}</th>'
        cal += f'</tr></thead>\n'
        
        # Ajout des jours du mois
        cal += '<tbody>\n'
        for week in self.cal:
            cal += f'{self.formatweek(week, activites)}\n'
        cal += '</tbody>\n'
        
        cal += '</table>'
        return cal

@login_required
def calendrier_activites(request):
    # Récupérer le mois et l'année à afficher
    d = get_date(request.GET.get('month', None))
    
    # Instance de notre classe Calendar
    cal = Calendar(d.year, d.month)
    html_calendar = cal.formatmonth(withyear=True)
    
    # Calculer les mois précédent et suivant
    prev_month = prev_month_link(d)
    next_month = next_month_link(d)
    
    context = {
        'calendar': mark_safe(html_calendar),
        'prev_month': prev_month,
        'next_month': next_month,
    }
    
    return render(request, 'activites/calendrier.html', context)

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return date.today()

def prev_month_link(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month_link(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month



from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserPasswordChangeForm

@login_required
def change_password(request):
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour maintenir la session
            messages.success(request, 'Votre mot de passe a été changé avec succès!')
            return redirect('profile')
    else:
        form = UserPasswordChangeForm(request.user)
    return render(request, 'auth/change_password.html', {'form': form})


# Responsable Views
@login_required
def responsable_list(request):
    responsables = Responsable.objects.all()
    return render(request, 'responsables/list.html', {'responsables': responsables})

@login_required
def responsable_detail(request, pk):
    responsable = get_object_or_404(Responsable, pk=pk)
    activites = Activite.objects.filter(responsable=responsable)
    return render(request, 'responsables/detail.html', {'responsable': responsable, 'activites': activites})

@login_required
def responsable_create(request):
    if request.method == 'POST':
        form = ResponsableForm(request.POST)
        if form.is_valid():
            responsable = form.save(commit=False)
            responsable.created_by = request.user
            responsable.save()
            messages.success(request, f"Responsable {responsable} ajouté avec succès!")
            return redirect('responsable_list')
    else:
        form = ResponsableForm()
    
    return render(request, 'responsables/create.html', {'form': form})

@login_required
def responsable_edit(request, pk):
    responsable = get_object_or_404(Responsable, pk=pk)
    if request.method == 'POST':
        form = ResponsableForm(request.POST, instance=responsable)
        if form.is_valid():
            form.save()
            messages.success(request, f"Responsable {responsable} modifié avec succès!")
            return redirect('responsable_detail', pk=responsable.pk)
    else:
        form = ResponsableForm(instance=responsable)
    
    return render(request, 'responsables/edit.html', {'form': form, 'responsable': responsable})

@login_required
def responsable_delete(request, pk):
    responsable = get_object_or_404(Responsable, pk=pk)
    if request.method == 'POST':
        nom = responsable.nom
        responsable.delete()
        messages.success(request, f"Responsable {nom} supprimé avec succès!")
        return redirect('responsable_list')
    
    return render(request, 'responsables/delete.html', {'responsable': responsable})

# Animateur Views
@login_required
def animateur_list(request):
    animateurs = Animateur.objects.all()
    return render(request, 'animateurs/list.html', {'animateurs': animateurs})

@login_required
def animateur_detail(request, pk):
    animateur = get_object_or_404(Animateur, pk=pk)
    activites = Activite.objects.filter(animateurs=animateur)
    return render(request, 'animateurs/detail.html', {'animateur': animateur, 'activites': activites})

@login_required
def animateur_create(request):
    if request.method == 'POST':
        form = AnimateurForm(request.POST)
        if form.is_valid():
            animateur = form.save(commit=False)
            animateur.created_by = request.user
            animateur.save()
            messages.success(request, f"Animateur {animateur} ajouté avec succès!")
            return redirect('animateur_list')
    else:
        form = AnimateurForm()
    
    return render(request, 'animateurs/create.html', {'form': form})

@login_required
def animateur_edit(request, pk):
    animateur = get_object_or_404(Animateur, pk=pk)
    if request.method == 'POST':
        form = AnimateurForm(request.POST, instance=animateur)
        if form.is_valid():
            form.save()
            messages.success(request, f"Animateur {animateur} modifié avec succès!")
            return redirect('animateur_detail', pk=animateur.pk)
    else:
        form = AnimateurForm(instance=animateur)
    
    return render(request, 'animateurs/edit.html', {'form': form, 'animateur': animateur})

@login_required
def animateur_delete(request, pk):
    animateur = get_object_or_404(Animateur, pk=pk)
    if request.method == 'POST':
        nom = animateur.nom
        animateur.delete()
        messages.success(request, f"Animateur {nom} supprimé avec succès!")
        return redirect('animateur_list')
    
    return render(request, 'animateurs/delete.html', {'animateur': animateur})

# Infrastructure Views
@login_required
def infrastructure_list(request):
    infrastructures = Infrastructure.objects.all()
    return render(request, 'infrastructures/list.html', {'infrastructures': infrastructures})

@login_required
def infrastructure_detail(request, pk):
    infrastructure = get_object_or_404(Infrastructure, pk=pk)
    activites = Activite.objects.filter(infrastructure=infrastructure)
    return render(request, 'infrastructures/detail.html', {'infrastructure': infrastructure, 'activites': activites})

@login_required
def infrastructure_create(request):
    if request.method == 'POST':
        form = InfrastructureForm(request.POST)
        if form.is_valid():
            infrastructure = form.save(commit=False)
            infrastructure.created_by = request.user
            infrastructure.save()
            messages.success(request, f"Infrastructure {infrastructure} ajoutée avec succès!")
            return redirect('infrastructure_list')
    else:
        form = InfrastructureForm()
    
    return render(request, 'infrastructures/create.html', {'form': form})

@login_required
def infrastructure_edit(request, pk):
    infrastructure = get_object_or_404(Infrastructure, pk=pk)
    if request.method == 'POST':
        form = InfrastructureForm(request.POST, instance=infrastructure)
        if form.is_valid():
            form.save()
            messages.success(request, f"Infrastructure {infrastructure} modifiée avec succès!")
            return redirect('infrastructure_detail', pk=infrastructure.pk)
    else:
        form = InfrastructureForm(instance=infrastructure)
    
    return render(request, 'infrastructures/edit.html', {'form': form, 'infrastructure': infrastructure})

@login_required
def infrastructure_delete(request, pk):
    infrastructure = get_object_or_404(Infrastructure, pk=pk)
    if request.method == 'POST':
        nom = infrastructure.nom
        infrastructure.delete()
        messages.success(request, f"Infrastructure {nom} supprimée avec succès!")
        return redirect('infrastructure_list')
    
    return render(request, 'infrastructures/delete.html', {'infrastructure': infrastructure})

# Matériel Views
@login_required
def materiel_list(request):
    materiels = Materiel.objects.all()
    return render(request, 'materiel/list.html', {'materiels': materiels})

@login_required
def materiel_detail(request, pk):
    materiel = get_object_or_404(Materiel, pk=pk)
    activites = Activite.objects.filter(materiels=materiel)
    return render(request, 'materiel/detail.html', {'materiel': materiel, 'activites': activites})

@login_required
def materiel_create(request):
    if request.method == 'POST':
        form = MaterielForm(request.POST)
        if form.is_valid():
            materiel = form.save(commit=False)
            materiel.created_by = request.user
            materiel.save()
            messages.success(request, f"Matériel {materiel} ajouté avec succès!")
            return redirect('materiel_list')
    else:
        form = MaterielForm()
    
    return render(request, 'materiel/create.html', {'form': form})

@login_required
def materiel_edit(request, pk):
    materiel = get_object_or_404(Materiel, pk=pk)
    if request.method == 'POST':
        form = MaterielForm(request.POST, instance=materiel)
        if form.is_valid():
            form.save()
            messages.success(request, f"Matériel {materiel} modifié avec succès!")
            return redirect('materiel_detail', pk=materiel.pk)
    else:
        form = MaterielForm(instance=materiel)
    
    return render(request, 'materiel/edit.html', {'form': form, 'materiel': materiel})

@login_required
def materiel_delete(request, pk):
    materiel = get_object_or_404(Materiel, pk=pk)
    if request.method == 'POST':
        nom = materiel.nom
        materiel.delete()
        messages.success(request, f"Matériel {nom} supprimé avec succès!")
        return redirect('materiel_list')
    
    return render(request, 'materiel/delete.html', {'materiel': materiel})


@login_required
def inscription_create(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            activite = form.cleaned_data['activite']
            participant = form.cleaned_data['participant']
            
            # Vérifier si l'activité est complète
            if activite.est_complete():
                messages.error(request, f"L'activité {activite} est complète!")
                return redirect('activite_detail', pk=activite.pk)
            
            # Vérifier si le participant est déjà inscrit (sans utiliser est_inscrit)
            if Inscription.objects.filter(participant=participant, activite=activite).exists():
                messages.error(request, f"{participant} est déjà inscrit à cette activité!")
                return redirect('activite_detail', pk=activite.pk)
            
            inscription = form.save(commit=False)
            inscription.created_by = request.user
            inscription.save()
            
            messages.success(request, f"Inscription de {participant} à {activite} réussie!")
            
            # Si la requête provient de la page d'activité, rediriger vers cette activité
            if 'activite_id' in request.POST:
                return redirect('activite_detail', pk=request.POST['activite_id'])
            # Sinon, rediriger vers les détails du participant
            else:
                return redirect('participant_detail', pk=participant.pk)
    else:
        # Pré-remplir avec l'activité ou le participant si fourni dans l'URL
        initial = {}
        if 'activite_id' in request.GET:
            initial['activite'] = request.GET['activite_id']
        if 'participant_id' in request.GET:
            initial['participant'] = request.GET['participant_id']
        
        form = InscriptionForm(initial=initial)
    
    return render(request, 'inscriptions/create.html', {'form': form})

