import calendar
from django.views.generic import ListView
from .models import Budget
from transactions.models import Category
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .forms import BudgetForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.paginator import Paginator
from typing import Any
from transactions.models import Transaction
from transactions.forms import TransactionForm
PAGINATION_SIZE = 10
# Create your views here.
class BudgetsDashboardView(ListView):
    model = Budget
    template_name = 'budgets/budgets.html'
    context_object_name = 'budgets'
    paginate_by = PAGINATION_SIZE

    def get_queryset(self):
        queryset = Budget.objects.filter(user=self.request.user)

        category = self.request.GET.get('category')
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')

        if category:
            queryset = queryset.filter(category=category)
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for budget in context['budgets']:
            budget.month_name = calendar.month_name[budget.month]
        # Add filter options
        context['categories'] = Category.objects.all()
        context['months'] = [(i, calendar.month_name[i]) for i in range(1, 13)]
        context['years'] = Budget.objects.filter(user=self.request.user).values_list('year', flat=True).distinct().order_by('-year')
        # Add current filter values
        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('Hx-Request') == 'true':
            html = render_to_string('budgets/partials/budgets_table.html', context, request=self.request)
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)
  

class BudgetCreateView(CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = "budgets/partials/budgets_table.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # To render the whole transaction tabel, paginated transactions are required  
        budgets = Budget.objects.filter(user=self.request.user)
        total_budget_limit = sum(budget.amount for budget in budgets)
        count = budgets.count()
        paginator = Paginator(budgets, PAGINATION_SIZE)
        page_obj = paginator.get_page(1)
        # Merge the existing context dict with the new one
        context.update({
            "page_obj": page_obj,
            "paginator": paginator,
            "budgets": page_obj.object_list,
            "is_paginated": paginator.num_pages > 1,
            "total_budget_limit": total_budget_limit,
            "count": count,
        })

        return context

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        messages.success(self.request, "Budget added successfully!")
        if self.request.htmx:
            # htmx-oob is used to update multiple elements (table and messages) which are not in the same container  
            context['is_oob'] = True
            table_html = render_to_string("budgets/partials/budgets_table.html", context, request=self.request)
            message_html = render_to_string("budgets/components/messages.html", context, request=self.request)
            return HttpResponse(f"{table_html}{message_html}")

        return super().render_to_response(context)


def open_budget_create_modal(request):
    form = BudgetForm()
    context = {
        'form': form,
        'budget': None,  # Explicitly pass None for create
    }
    return render(request, "budgets/components/budgets_modal.html", context=context)

def open_budget_update_modal(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)  # Ensure user owns the budget
    form = BudgetForm(instance=budget)
    context = {
        'form': form,
        'budget': budget,  # Pass the budget for update
    }
    return render(request, "budgets/components/budgets_modal.html", context=context)
    
def close_modal(request):
    return render(request, "budgets/components/modal_placeholder.html")
    