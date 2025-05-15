from django.urls import path
from .views import BudgetsDashboardView, open_budget_create_modal, open_budget_update_modal

urlpatterns = [
    path('', BudgetsDashboardView.as_view(), name='budgets_dashboard'),
    path('create/', open_budget_create_modal, name='open_budget_create_modal'),
    path('update/<int:pk>/', open_budget_update_modal, name='open_budget_update_modal'),
]

