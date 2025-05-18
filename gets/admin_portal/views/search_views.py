# admin_portal/views/search_views.py
from django.views.generic import FormView
from common.forms.search_forms import AdvancedSearchForm
from common.services.search_service import SearchService
from admin_portal.mixins import AdminStaffRequiredMixin

class RecherceAdvancedView(AdminStaffRequiredMixin, FormView):
    template_name = 'admin_portal/recherche/resultats.html'
    form_class = AdvancedSearchForm
    
    def get_initial(self):
        initial = super().get_initial()
        initial['query'] = self.request.GET.get('query', '')
        initial['entity_type'] = self.request.GET.get('entity_type', 'all')
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        query = self.request.GET.get('query', '')
        entity_type = self.request.GET.get('entity_type', 'all')
        
        context['query'] = query
        context['type_recherche'] = entity_type
        
        if query:
            results = SearchService.search_by_type(query, entity_type)
            for key, value in results.items():
                context[key] = value
        
        return context