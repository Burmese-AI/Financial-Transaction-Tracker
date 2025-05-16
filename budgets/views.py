import calendar
from django.views.generic import ListView
from .models import Budget
from transactions.models import Category
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .forms import BudgetForm
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.paginator import Paginator
from typing import Any
from transactions.models import Transaction
from transactions.forms import TransactionForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeleteView
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear

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
            # Calculate total expenses for this budget's category, month, year, and user
            expense = Transaction.objects.filter(
                user=budget.user,
                category=budget.category,
                type='expense'
            ).annotate(
                txn_month=ExtractMonth('created_at'),
                txn_year=ExtractYear('created_at')
            ).filter(
                txn_month=budget.month,
                txn_year=budget.year
            ).aggregate(total=Sum('amount'))['total'] or 0
            budget.expense = expense
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
        try:
            # Check if budget already exists for this category, month, and year
            existing_budget = Budget.objects.filter(
                user=self.request.user,
                category=form.cleaned_data['category'],
                month=form.cleaned_data['month'],
                year=form.cleaned_data['year']
            ).first()
            
            if existing_budget:
                messages.error(
                    self.request, 
                    f"A budget for {form.cleaned_data['category']} in {calendar.month_name[form.cleaned_data['month']]} {form.cleaned_data['year']} already exists."
                )
                return self.render_to_response(self.get_context_data(form=form))

            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            messages.success(self.request, "Budget added successfully")
            return self.render_to_response(self.get_context_data())
        except Exception as e:
            messages.error(
                self.request,
                "An error occurred while creating the budget. Please try again."
            )
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            if field == '__all__':
                error_messages.append(" ".join(errors))
            else:
                field_name = form.fields[field].label or field.replace('_', ' ').title()
                error_messages.append(f"{field_name}: {' '.join(errors)}")
        
        if error_messages:
            messages.error(self.request, "Please correct the following errors:\n" + "\n".join(error_messages))
        else:
            messages.error(self.request, "Please correct the errors below.")
            
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            budgets = Budget.objects.filter(user=self.request.user)
            paginator = Paginator(budgets, PAGINATION_SIZE)
            page_obj = paginator.get_page(1)
            context.update({
                "page_obj": page_obj,
                "paginator": paginator,
                "budgets": page_obj.object_list,
                "is_paginated": paginator.num_pages > 1,
            })
            # Add month_name to each budget
            for budget in context['budgets']:
                budget.month_name = calendar.month_name[budget.month]
            return context
        except Exception as e:
            messages.error(self.request, "An error occurred while loading the page. Please refresh and try again.")
            return super().get_context_data(**kwargs)

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        try:
            if self.request.htmx:
                # htmx-oob is used to update multiple elements (table and messages) which are not in the same container  
                context['is_oob'] = True
                table_html = render_to_string("budgets/partials/budgets_table.html", context, request=self.request)
                message_html = render_to_string("budgets/components/messages.html", context, request=self.request)
                return HttpResponse(f"{table_html}{message_html}")

            return super().render_to_response(context)
        except Exception as e:
            messages.error(self.request, "An error occurred while updating the page. Please refresh and try again.")
            return super().render_to_response(context)

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = "budgets/partials/budgets_table.html"
    
    def get_queryset(self):
        # Ensuring User can only update their own budgets
        return Budget.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        try:
            # Do NOT update self.object yet
            temp_object = form.save(commit=False)
            existing_budget = Budget.objects.filter(
                user=self.request.user,
                category=form.cleaned_data['category'],
                month=form.cleaned_data['month'],
                year=form.cleaned_data['year']
            ).exclude(pk=temp_object.pk).first()
            
            if existing_budget:
                messages.error(
                    self.request, 
                    f"A budget for {form.cleaned_data['category']} in {calendar.month_name[form.cleaned_data['month']]} {form.cleaned_data['year']} already exists."
                )
                # Re-fetch the original object from the database to avoid showing unsaved changes
                original_object = Budget.objects.get(pk=temp_object.pk)
                context = self.get_context_data(form=form)
                context['budget'] = original_object
                context['budget'].month_name = calendar.month_name[original_object.month]
                return self.render_to_response(context)
            
            # Only now update self.object and save
            self.object = temp_object
            self.object.save()
            messages.success(self.request, "Budget updated successfully!")
            return self.render_to_response(self.get_context_data())
        except Exception as e:
            messages.error(self.request, "An error occurred while updating the budget. Please try again.")
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['budget'] = self.object
        context['budget'].month_name = calendar.month_name[context['budget'].month]
        return context
    
    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.htmx:
            # htmx-oob is used to update multiple elements (table and messages) which are not in the same container  
            context['is_oob'] = True
            budget_html = render_to_string("budgets/partials/budget_row.html", context, request=self.request)
            message_html = render_to_string("budgets/components/messages.html", context, request=self.request)
            return HttpResponse(f"{budget_html}{message_html}")
        return super().render_to_response(context, **response_kwargs)

class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    model = Budget
    template_name = "budgets/partials/budgets_table.html"
    success_url = reverse_lazy('budgets')
    
    def get_queryset(self):
        # Ensuring User can only update their own transactions
        return Budget.objects.filter(user=self.request.user)
    
    # DeleteView doesn't utilize render_to_response like other views due to success_url, 
    # So, override the form_valid method where deletion occurs and change the return
    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        return self.render_to_response(self.get_context_data())
    
    def get_context_data(self, **kwargs):
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

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        messages.success(self.request, "Budget deleted successfully!")
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
    