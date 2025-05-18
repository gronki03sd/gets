# admin_portal/views/animateur_views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render

from common.models import Animateur
from common.forms.animateur_forms import AnimateurForm
from common.services.animateur_service import AnimateurService
from admin_portal.mixins import AdminStaffRequiredMixin

class AnimateurListView(AdminStaffRequiredMixin, ListView):
    model = Animateur
    template_name = 'admin_portal/animateurs/list.html'
    context_object_name = 'animateurs'
    
    def get_queryset(self):
        return AnimateurService.get_all_animateurs()

def animateur_search(request):
    search_query = request.GET.get('q', '')
    animateurs = AnimateurService.search_animateurs(search_query)
    return render(request, 'admin_portal/animateurs/partials/animateur_list.html', {'animateurs': animateurs})

class AnimateurDetailView(AdminStaffRequiredMixin, DetailView):
    model = Animateur
    template_name = 'admin_portal/animateurs/detail.html'
    context_object_name = 'animateur'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activites'] = self.object.activites.all()
        return context

class AnimateurCreateView(AdminStaffRequiredMixin, CreateView):
    model = Animateur
    form_class = AnimateurForm
    template_name = 'admin_portal/animateurs/create.html'
    success_url = reverse_lazy('admin_portal:animateur_list')
    
    def form_valid(self, form):
        animateur = AnimateurService.create_animateur(form, self.request.user)
        messages.success(self.request, f"Animateur {animateur} ajouté avec succès!")
        return redirect(self.success_url)

class AnimateurUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = Animateur
    form_class = AnimateurForm
    template_name = 'admin_portal/animateurs/edit.html'
    
    def get_success_url(self):
        return reverse_lazy('admin_portal:animateur_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        animateur = AnimateurService.update_animateur(self.object.pk, form)
        messages.success(self.request, f"Animateur {animateur} modifié avec succès!")
        return redirect(self.get_success_url())

class AnimateurDeleteView(AdminStaffRequiredMixin, DeleteView):
    model = Animateur
    template_name = 'admin_portal/animateurs/delete.html'
    success_url = reverse_lazy('admin_portal:animateur_list')
    context_object_name = 'animateur'
    
    def delete(self, request, *args, **kwargs):
        animateur = self.get_object()
        message = f"Animateur {animateur} supprimé avec succès!"
        AnimateurService.delete_animateur(animateur.pk)
        messages.success(self.request, message)
        return redirect(self.success_url)