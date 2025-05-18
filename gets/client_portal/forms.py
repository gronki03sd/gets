# client_portal/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from common.models import User, Participant

class ClientRegisterForm(UserCreationForm):
    """Form for client user registration"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    user_type = forms.ChoiceField(
        choices=[('participant', 'Participant'), ('animateur', 'Moniteur')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='participant'
    )
    
    class Meta:
        model = User
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
            
            # Import here to avoid circular imports
            from django.utils import timezone
            from common.models import Participant, Animateur
            
            # Create participant or animator profile based on selection
            if self.cleaned_data['user_type'] == 'participant':
                Participant.objects.create(
                    nom=self.cleaned_data['last_name'],
                    prenom=self.cleaned_data['first_name'],
                    date_naissance=timezone.now().date(),  # Default value, can be updated later
                    email=self.cleaned_data['email'],
                    telephone=self.cleaned_data.get('phone_number', ''),
                    created_by=user
                )
            elif self.cleaned_data['user_type'] == 'animateur':
                Animateur.objects.create(
                    nom=self.cleaned_data['last_name'],
                    prenom=self.cleaned_data['first_name'],
                    email=self.cleaned_data['email'],
                    telephone=self.cleaned_data.get('phone_number', ''),
                    created_by=user
                )
                
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
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_image']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ClientParticipantForm(forms.ModelForm):
    """Form for client participant info"""
    class Meta:
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