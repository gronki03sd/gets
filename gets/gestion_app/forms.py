# For forms.py - fix the import timing issue

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm

# Don't import models at the module level directly
# Instead, get them inside the class definitions

# User model should be imported like this to avoid early loading:
User = None
def get_user_model_safely():
    global User
    if User is None:
        from django.contrib.auth import get_user_model
        User = get_user_model()
    return User

# Admin User Authentication Forms
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = get_user_model_safely()
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # Add bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

class ClientRegistrationForm(UserCreationForm):
    """Registration form for clients (participants and animators)"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    user_type = forms.ChoiceField(
        choices=[('participant', 'Participant'), ('animateur', 'Moniteur')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='participant'
    )
    
    class Meta:
        model = get_user_model_safely()
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ClientRegistrationForm, self).__init__(*args, **kwargs)
        # Add bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'staff'  # Default role for all client registrations
        
        if commit:
            user.save()
            
            # Import these here to avoid circular imports
            from django.utils import timezone
            from .models import Participant, Animateur
            
            # Create participant or animator profile based on selection
            if self.cleaned_data['user_type'] == 'participant':
                Participant.objects.create(
                    nom=self.cleaned_data['last_name'],
                    prenom=self.cleaned_data['first_name'],
                    date_naissance=timezone.now().date(),  # Default value, can be updated later
                    email=self.cleaned_data['email'],
                    created_by=user
                )
            elif self.cleaned_data['user_type'] == 'animateur':
                Animateur.objects.create(
                    nom=self.cleaned_data['last_name'],
                    prenom=self.cleaned_data['first_name'],
                    email=self.cleaned_data['email'],
                    telephone='',  # Default empty value, can be updated later
                    created_by=user
                )
                
        return user
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model_safely()
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_image']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


# Main Application Forms
class ParticipantForm(forms.ModelForm):
    class Meta:
        from .models import Participant
        model = Participant
        fields = ['nom', 'prenom', 'date_naissance', 'adresse', 'telephone', 'email']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ActiviteSearchForm(forms.Form):
    date_debut = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date"
    )
    nom = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nom de l\'activité',
            'hx-get': '/activites/search/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#activite-list'
        }),
        label="Nom"
    )


from django.forms import ModelForm, DateTimeInput, SelectMultiple

class CustomDateTimeInput(DateTimeInput):
    input_type = 'datetime-local'

class ActiviteForm(ModelForm):
    class Meta:
        from .models import Activite
        model = Activite
        fields = ['nom', 'description', 'duree', 'date_debut', 'responsable', 'infrastructure', 
                  'capacite_max', 'animateurs', 'materiels']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'duree': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'date_debut': CustomDateTimeInput(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'infrastructure': forms.Select(attrs={'class': 'form-select'}),
            'capacite_max': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'animateurs': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'materiels': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        duree = cleaned_data.get('duree')
        
        # Vérifiez que la durée est positive
        if duree and duree <= 0:
            self.add_error('duree', "La durée doit être supérieure à 0 minutes.")
        
        # Vérifiez la disponibilité de l'infrastructure
        infrastructure = cleaned_data.get('infrastructure')
        if infrastructure and not infrastructure.disponible:
            self.add_error('infrastructure', "Cette infrastructure n'est pas disponible.")
        
        # Vérifiez la disponibilité des matériels
        materiels = cleaned_data.get('materiels')
        if materiels:
            for materiel in materiels:
                if materiel.quantite_disponible <= 0:
                    self.add_error('materiels', f"Le matériel '{materiel.nom}' n'est pas disponible en quantité suffisante.")
        
        return cleaned_data

# Formulaires pour les matériels et animateurs à utiliser dans les vues inline
class ActiviteMaterielForm(forms.ModelForm):
    class Meta:
        from .models import Activite
        model = Activite.materiels.through
        fields = ['materiel', 'quantite_requise']
        widgets = {
            'materiel': forms.Select(attrs={'class': 'form-select'}),
            'quantite_requise': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
        }

class ActiviteAnimateurForm(forms.ModelForm):
    class Meta:
        from .models import Activite
        model = Activite.animateurs.through
        fields = ['animateur']
        widgets = {
            'animateur': forms.Select(attrs={'class': 'form-select'})
        }


class InscriptionForm(forms.ModelForm):
    class Meta:
        from .models import Inscription
        model = Inscription
        fields = ['participant', 'activite', 'statut']
        widgets = {
            'participant': forms.Select(attrs={'class': 'form-select'}),
            'activite': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

class ResponsableForm(forms.ModelForm):
    class Meta:
        from .models import Responsable
        model = Responsable
        fields = ['nom', 'prenom', 'specialite', 'telephone', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'specialite': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class AnimateurForm(forms.ModelForm):
    class Meta:
        from .models import Animateur
        model = Animateur
        fields = ['nom', 'prenom', 'competence', 'telephone', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'competence': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class InfrastructureForm(forms.ModelForm):
    class Meta:
        from .models import Infrastructure
        model = Infrastructure
        fields = ['nom', 'type', 'capacite', 'localisation', 'disponible']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'capacite': forms.NumberInput(attrs={'class': 'form-control'}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MaterielForm(forms.ModelForm):
    class Meta:
        from .models import Materiel
        model = Materiel
        fields = ['nom', 'description', 'quantite_disponible']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantite_disponible': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# New client-specific forms
class ClientRegisterForm(UserCreationForm):
    """Form for client user registration"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = get_user_model_safely()
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ClientRegisterForm, self).__init__(*args, **kwargs)
        # Add bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Set role to 'staff' by default for client users
        self.initial['role'] = 'staff'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'staff'  # Ensure client users are always 'staff' role
        if commit:
            user.save()
        return user

class ClientLoginForm(AuthenticationForm):
    """Form for client login"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Nom d'utilisateur"
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Mot de passe'
    }))
    
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)

class ClientProfileForm(forms.ModelForm):
    """Form for client profile editing"""
    class Meta:
        model = get_user_model_safely()
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_image']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ClientInscriptionForm(forms.ModelForm):
    """Form for client event registration"""
    class Meta:
        from .models import Inscription
        model = Inscription
        fields = ['activite']
        widgets = {
            'activite': forms.HiddenInput(),  # Hidden because we'll set this from the URL
        }

class ContactForm(forms.Form):
    """Contact form for clients"""
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Votre nom'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Votre email'
    }))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Sujet'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Votre message',
        'rows': 5
    }))

class EventSearchForm(forms.Form):
    """Form for searching events on the client side"""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control me-2',
        'placeholder': 'Rechercher un événement...',
        'aria-label': 'Search'
    }))
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))