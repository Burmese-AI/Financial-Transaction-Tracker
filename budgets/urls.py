from django.urls import path
from .views import BudgetsDashboardView

urlpatterns = [
    path('', BudgetsDashboardView.as_view(), name='budgets_dashboard'),
]

