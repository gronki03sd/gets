# common/forms/infrastructure_forms.py
from django import forms
from common.models import Infrastructure

class InfrastructureForm(forms.ModelForm):
    class Meta:
        model = Infrastructure
        fields = ['nom', 'type', 'capacite', 'localisation', 'disponible']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'capacite': forms.NumberInput(attrs={'class': 'form-control'}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class InfrastructureSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Rechercher une infrastructure...',
            'hx-get': '/admin/infrastructures/search/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#infrastructure-list'
        })
    )
    disponible = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'hx-get': '/admin/infrastructures/search/',
            'hx-trigger': 'change',
            'hx-target': '#infrastructure-list'
        }),
        label="Afficher uniquement les infrastructures disponibles"
    )