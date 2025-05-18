# admin_portal/views/responsable_views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render

from common.models import Responsable
from common.forms.responsable_forms import ResponsableForm
from common.services.responsable_service import ResponsableService
from admin_portal.mixins import AdminStaffRequiredMixin

class ResponsableListView(AdminStaffRequiredMixin, ListView):
    model = Responsable
    template_name = 'admin_portal/responsables/list.html'
    context_object_name = 'responsables'
    
    def get_queryset(self):
        return ResponsableService.get_all_responsables()

def responsable_search(request):
    search_query = request.GET.get('q', '')
    responsables = ResponsableService.search_responsables(search_query)
    return render(request, 'admin_portal/responsables/partials/responsable_list.html', {'responsables': responsables})

class ResponsableDetailView(AdminStaffRequiredMixin, DetailView):
    model = Responsable
    template_name = 'admin_portal/responsables/detail.html'
    context_object_name = 'responsable'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activites'] = self.object.activites.all()
        return context

class ResponsableCreateView(AdminStaffRequiredMixin, CreateView):
    model = Responsable
    form_class = ResponsableForm
    template_name = 'admin_portal/responsables/create.html'
    success_url = reverse_lazy('admin_portal:responsable_list')
    
    def form_valid(self, form):
        responsable = ResponsableService.create_responsable(form, self.request.user)
        messages.success(self.request, f"Responsable {responsable} ajouté avec succès!")
        return redirect(self.success_url)

class ResponsableUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = Responsable
    form_class = ResponsableForm
    template_name = 'admin_portal/responsables/edit.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:responsable_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        responsable = ResponsableService.update_responsable(self.object.pk, form)
        messages.success(self.request, f"Responsable {responsable} modifié avec succès!")
        return redirect(self.get_success_url())

class ResponsableDeleteView(AdminStaffRequiredMixin, DeleteView):
    model = Responsable
    template_name = 'admin_portal/responsables/delete.html'
    success_url = reverse_lazy('admin_portal:responsable_list')
    context_object_name = 'responsable'
    
    def delete(self, request, *args, **kwargs):
        responsable = self.get_object()
        message = f"Responsable {responsable} supprimé avec succès!"
        ResponsableService.delete_responsable(responsable.pk)
        messages.success(self.request, message)
        return redirect(self.success_url)