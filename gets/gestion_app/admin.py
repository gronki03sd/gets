from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Participant, Activite, Responsable, Animateur, 
    Infrastructure, Materiel, Inscription, ActiviteAnimateur, ActiviteMateriel
)

# Personnalisation de l'interface admin pour User
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('role', 'phone_number', 'profile_image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {'fields': ('role', 'phone_number', 'profile_image')}),
    )
    list_filter = UserAdmin.list_filter + ('role',)

# Enregistrement des modèles
admin.site.register(User, CustomUserAdmin)
admin.site.register(Participant)
admin.site.register(Activite)
admin.site.register(Responsable)
admin.site.register(Animateur)
admin.site.register(Infrastructure)
admin.site.register(Materiel)
admin.site.register(Inscription)
admin.site.register(ActiviteAnimateur)
admin.site.register(ActiviteMateriel)