
from django.views.generic import ListView
from .models import Budget

PAGINATION_SIZE = 10
# Create your views here.
class BudgetsDashboardView(ListView):
    model = Budget
    template_name = 'budgets/budgets.html'
    context_object_name = 'budgets'
    paginate_by = PAGINATION_SIZE

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
  