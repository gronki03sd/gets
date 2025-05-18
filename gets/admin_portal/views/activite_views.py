# admin_portal/views/activite_views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
import calendar
from datetime import datetime, date, timedelta

from common.models import Activite
from common.forms.activite_forms import ActiviteForm, ActiviteSearchForm
from common.services.activite_service import ActiviteService
from common.services.calendar_service import CalendarService
from admin_portal.mixins import AdminStaffRequiredMixin

class ActiviteListView(AdminStaffRequiredMixin, ListView):
    model = Activite
    template_name = 'admin_portal/activites/list.html'
    context_object_name = 'activites'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ActiviteSearchForm()
        return context
    
    def get_queryset(self):
        return ActiviteService.get_all_activites()

def activite_search(request):
    """HTMX compatible view for searching activities"""
    form = ActiviteSearchForm(request.GET)
    
    date_debut = request.GET.get('date_debut')
    nom = request.GET.get('nom')
    
    activites = ActiviteService.search_activites(query=nom, date_debut=date_debut)
    
    return render(request, 'admin_portal/activites/partials/activite_list.html', {'activites': activites})

class ActiviteDetailView(AdminStaffRequiredMixin, DetailView):
    model = Activite
    template_name = 'admin_portal/activites/detail.html'
    context_object_name = 'activite'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inscriptions'] = self.object.inscriptions.all()
        context['materiels'] = self.object.activite_materiels.all()
        return context

class ActiviteCreateView(AdminStaffRequiredMixin, CreateView):
    model = Activite
    form_class = ActiviteForm
    template_name = 'admin_portal/activites/create.html'
    success_url = reverse_lazy('admin_portal:activite_list')
    
    def form_valid(self, form):
        activite = ActiviteService.create_activite(form, self.request.user)
        messages.success(self.request, f"Activité {activite} créée avec succès!")
        return redirect(self.success_url)

class ActiviteUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = Activite
    form_class = ActiviteForm
    template_name = 'admin_portal/activites/edit.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:activite_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        activite = ActiviteService.update_activite(self.object.pk, form)
        messages.success(self.request, f"Activité {activite} modifiée avec succès!")
        return redirect(self.get_success_url())

class ActiviteDeleteView(AdminStaffRequiredMixin, DeleteView):
    model = Activite
    template_name = 'admin_portal/activites/delete.html'
    success_url = reverse_lazy('admin_portal:activite_list')
    context_object_name = 'activite'
    
    def delete(self, request, *args, **kwargs):
        activite = self.get_object()
        message = f"Activité {activite} supprimée avec succès!"
        ActiviteService.delete_activite(activite.pk)
        messages.success(self.request, message)
        return redirect(self.success_url)

class CalendrierActivitesView(AdminStaffRequiredMixin, TemplateView):
    template_name = 'admin_portal/activites/calendrier.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = CalendarService.get_date_from_request(self.request.GET.get('month', None))
        calendar_data = CalendarService.get_month_calendar(d.year, d.month)
        context.update(calendar_data)
        return context