# admin_portal/views/materiel_views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render

from common.models import Materiel
from common.forms.materiel_forms import MaterielForm, MaterielSearchForm
from common.services.materiel_service import MaterielService
from admin_portal.mixins import AdminStaffRequiredMixin

class MaterielListView(AdminStaffRequiredMixin, ListView):
    model = Materiel
    template_name = 'admin_portal/materiel/list.html'
    context_object_name = 'materiels'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MaterielSearchForm()
        return context
    
    def get_queryset(self):
        return MaterielService.get_all_materiels()

def materiel_search(request):
    search_query = request.GET.get('q', '')
    materiels = MaterielService.search_materiels(search_query)
    return render(request, 'admin_portal/materiel/partials/materiel_list.html', {'materiels': materiels})

class MaterielDetailView(AdminStaffRequiredMixin, DetailView):
    model = Materiel
    template_name = 'admin_portal/materiel/detail.html'
    context_object_name = 'materiel'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activites'] = self.object.activites.all()
        return context

class MaterielCreateView(AdminStaffRequiredMixin, CreateView):
    model = Materiel
    form_class = MaterielForm
    template_name = 'admin_portal/materiel/create.html'
    success_url = reverse_lazy('admin_portal:materiel_list')
    
    def form_valid(self, form):
        materiel = MaterielService.create_materiel(form, self.request.user)
        messages.success(self.request, f"Matériel {materiel} ajouté avec succès!")
        return redirect(self.success_url)

class MaterielUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = Materiel
    form_class = MaterielForm
    template_name = 'admin_portal/materiel/edit.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:materiel_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        materiel = MaterielService.update_materiel(self.object.pk, form)
        messages.success(self.request, f"Matériel {materiel} modifié avec succès!")
        return redirect(self.get_success_url())

class MaterielDeleteView(AdminStaffRequiredMixin, DeleteView):
    model = Materiel
    template_name = 'admin_portal/materiel/delete.html'
    success_url = reverse_lazy('admin_portal:materiel_list')
    context_object_name = 'materiel'
    
    def delete(self, request, *args, **kwargs):
        materiel = self.get_object()
        message = f"Matériel {materiel} supprimé avec succès!"
        MaterielService.delete_materiel(materiel.pk)
        messages.success(self.request, message)
        return redirect(self.success_url)