# common/forms/animateur_forms.py
from django import forms
from common.models import Animateur

class AnimateurForm(forms.ModelForm):
    class Meta:
        model = Animateur
        fields = ['nom', 'prenom', 'competence', 'telephone', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'competence': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class AnimateurSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Rechercher un animateur...',
            'hx-get': '/admin/animateurs/search/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#animateur-list'
        })
    )