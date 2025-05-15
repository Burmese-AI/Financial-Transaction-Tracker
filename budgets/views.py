import calendar
from django.views.generic import ListView, CreateView
from .models import Budget
from transactions.models import Category
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .forms import BudgetForm
from django.core.paginator import Paginator
from typing import Any
from django.contrib import messages



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
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_month'] = self.request.GET.get('month', '')
        context['selected_year'] = self.request.GET.get('year', '')
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
        try:
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            messages.success(self.request, "Budget added successfully!")
            return self.render_to_response(self.get_context_data())
        except Exception as e:
            messages.error(self.request, f"Error creating budget: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        try:
            context = self.get_context_data(form=form)
            if self.request.headers.get('Hx-Request') == 'true':
                # Render the modal with form errors
                modal_html = render_to_string("budgets/components/budgets_modal.html", context, request=self.request)
                return HttpResponse(modal_html)
            return super().form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error processing form: {str(e)}")
            return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            # To render the whole transaction tabel, paginated transactions are required  
            budgets = Budget.objects.filter(user=self.request.user)
            paginator = Paginator(budgets, PAGINATION_SIZE)
            page_obj = paginator.get_page(1)
            # Merge the existing context dict with the new one
            context.update({
                "page_obj": page_obj,
                "paginator": paginator,
                "budgets": page_obj.object_list,
                "is_paginated": paginator.num_pages > 1,
            })
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading context: {str(e)}")
            return super().get_context_data(**kwargs)

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        try:
            if self.request.headers.get('Hx-Request') == 'true':
                # htmx-oob is used to update multiple elements (table and messages) which are not in the same container  
                context['is_oob'] = True
                table_html = render_to_string("budgets/partials/budgets_table.html", context, request=self.request)
                message_html = render_to_string("budgets/components/messages.html", context, request=self.request)
                return HttpResponse(f"{table_html}{message_html}")
            return super().render_to_response(context, **response_kwargs)
        except Exception as e:
            messages.error(self.request, f"Error rendering response: {str(e)}")
            return super().render_to_response(context, **response_kwargs)







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
    