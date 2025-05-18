# common/forms/activite_forms.py
from django import forms
from django.forms import ModelForm, DateTimeInput, SelectMultiple
from common.models import Activite

class CustomDateTimeInput(DateTimeInput):
    input_type = 'datetime-local'

class ActiviteForm(ModelForm):
    class Meta:
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
            'hx-get': '/admin/activites/search/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#activite-list'
        }),
        label="Nom"
    )

class ActiviteMaterielForm(forms.ModelForm):
    class Meta:
        model = Activite.materiels.through
        fields = ['materiel', 'quantite_requise']
        widgets = {
            'materiel': forms.Select(attrs={'class': 'form-select'}),
            'quantite_requise': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
        }

class ActiviteAnimateurForm(forms.ModelForm):
    class Meta:
        model = Activite.animateurs.through
        fields = ['animateur']
        widgets = {
            'animateur': forms.Select(attrs={'class': 'form-select'})
        }