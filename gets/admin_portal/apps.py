# admin_portal/apps.py
from django.apps import AppConfig

class AdminPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_portal'
    verbose_name = 'Administration Portal'