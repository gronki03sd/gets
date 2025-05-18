# common/forms/responsable_forms.py
from django import forms
from common.models import Responsable

class ResponsableForm(forms.ModelForm):
    class Meta:
        model = Responsable
        fields = ['nom', 'prenom', 'specialite', 'telephone', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'specialite': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ResponsableSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Rechercher un responsable...',
            'hx-get': '/admin/responsables/search/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#responsable-list'
        })
    )