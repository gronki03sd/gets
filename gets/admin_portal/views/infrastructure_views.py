# admin_portal/views/infrastructure_views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render

from common.models import Infrastructure
from common.forms.infrastructure_forms import InfrastructureForm, InfrastructureSearchForm
from common.services.infrastructure_service import InfrastructureService
from admin_portal.mixins import AdminStaffRequiredMixin

class InfrastructureListView(AdminStaffRequiredMixin, ListView):
    model = Infrastructure
    template_name = 'admin_portal/infrastructures/list.html'
    context_object_name = 'infrastructures'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InfrastructureSearchForm()
        return context
    
    def get_queryset(self):
        return InfrastructureService.get_all_infrastructures()

def infrastructure_search(request):
    search_query = request.GET.get('q', '')
    disponible_only = request.GET.get('disponible') == 'on'
    infrastructures = InfrastructureService.search_infrastructures(search_query, disponible_only)
    return render(request, 'admin_portal/infrastructures/partials/infrastructure_list.html', {'infrastructures': infrastructures})

class InfrastructureDetailView(AdminStaffRequiredMixin, DetailView):
    model = Infrastructure
    template_name = 'admin_portal/infrastructures/detail.html'
    context_object_name = 'infrastructure'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activites'] = self.object.activites.all()
        return context

class InfrastructureCreateView(AdminStaffRequiredMixin, CreateView):
    model = Infrastructure
    form_class = InfrastructureForm
    template_name = 'admin_portal/infrastructures/create.html'
    success_url = reverse_lazy('admin_portal:infrastructure_list')
    
    def form_valid(self, form):
        infrastructure = InfrastructureService.create_infrastructure(form, self.request.user)
        messages.success(self.request, f"Infrastructure {infrastructure} ajoutée avec succès!")
        return redirect(self.success_url)

class InfrastructureUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = Infrastructure
    form_class = InfrastructureForm
    template_name = 'admin_portal/infrastructures/edit.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:infrastructure_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        infrastructure = InfrastructureService.update_infrastructure(self.object.pk, form)
        messages.success(self.request, f"Infrastructure {infrastructure} modifiée avec succès!")
        return redirect(self.get_success_url())

class InfrastructureDeleteView(AdminStaffRequiredMixin, DeleteView):
    model = Infrastructure
    template_name = 'admin_portal/infrastructures/delete.html'
    success_url = reverse_lazy('admin_portal:infrastructure_list')
    context_object_name = 'infrastructure'
    
    def delete(self, request, *args, **kwargs):
        infrastructure = self.get_object()
        message = f"Infrastructure {infrastructure} supprimée avec succès!"
        InfrastructureService.delete_infrastructure(infrastructure.pk)
        messages.success(self.request, message)
        return redirect(self.success_url)