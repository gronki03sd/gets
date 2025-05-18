# common/forms/inscription_forms.py
from django import forms
from common.models import Inscription

class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['participant', 'activite', 'statut']
        widgets = {
            'participant': forms.Select(attrs={'class': 'form-select'}),
            'activite': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

class ClientInscriptionForm(forms.ModelForm):
    """Form for client event registration"""
    class Meta:
        model = Inscription
        fields = ['activite']
        widgets = {
            'activite': forms.HiddenInput(),  # Hidden because we'll set this from the URL
        }