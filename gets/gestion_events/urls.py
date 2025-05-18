# gestion_events/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_client_home(request):
    return redirect('client_portal:home')

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Django admin site
    path('admin/', include('admin_portal.urls', namespace='admin_portal')),  # Our custom admin portal
    path('', include('client_portal.urls', namespace='client_portal')),  # Client-facing portal
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)