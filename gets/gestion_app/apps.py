# Update your apps.py file to ensure proper initialization

from django.apps import AppConfig


class GestionAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_app'
    verbose_name = 'Gestion des events'
    
    def ready(self):
        """
        Override this method to perform initialization when Django is ready
        """
        # Import signals or other modules that should be loaded when Django is ready
        # For example: import gestion_app.signals
        pass