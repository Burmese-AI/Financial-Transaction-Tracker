from django.urls import path
from .views import BudgetsDashboardView, open_budget_create_modal, open_budget_update_modal, BudgetCreateView, BudgetDeleteView

urlpatterns = [
    path('', BudgetsDashboardView.as_view(), name='budgets_dashboard'),
    path('modal/', open_budget_create_modal, name='open_budget_create_modal'),
    path('modal/<uuid:pk>/', open_budget_update_modal, name='open_budget_update_modal'),
    path('create/', BudgetCreateView.as_view(), name='budget_create'),
    path('delete/<uuid:pk>/', BudgetDeleteView.as_view(), name='budget_delete'),
]

