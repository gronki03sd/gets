# common/forms/search_forms.py
from django import forms

class AdvancedSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Rechercher...'
        })
    )
    entity_type = forms.ChoiceField(
        choices=[
            ('all', 'Tout'),
            ('participants', 'Participants'),
            ('activites', 'Activités'),
            ('responsables', 'Responsables'),
            ('animateurs', 'Animateurs'),
            ('infrastructures', 'Infrastructures'),
            ('materiels', 'Matériel')
        ],
        initial='all',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )