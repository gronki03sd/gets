# common/forms/materiel_forms.py
from django import forms
from common.models import Materiel

class MaterielForm(forms.ModelForm):
    class Meta:
        model = Materiel
        fields = ['nom', 'description', 'quantite_disponible']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantite_disponible': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class MaterielSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Rechercher du matériel...',
            'hx-get': '/admin/materiel/search/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#materiel-list'
        })
    )