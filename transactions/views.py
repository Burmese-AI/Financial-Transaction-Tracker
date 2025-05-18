import json
import csv
from datetime import timedelta, datetime
from io import TextIOWrapper

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.contrib import messages
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse_lazy
from django.db.models import Q # For combining queries
from typing import Any
from .models import Transaction, Category
from budgets.models import Budget
from .forms import TransactionForm
from django.utils import timezone

PAGINATION_SIZE = 10

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'dashboard.html'
    context_object_name = 'transactions'
    paginate_by = PAGINATION_SIZE
    
    def get_queryset(self):
        query = Transaction.objects.filter(user=self.request.user)
        
        if self.request.GET.get('category'):
            query = query.filter(category__name__iexact=self.request.GET.get('category'))
        
        if self.request.GET.get('type'):
            query = query.filter(type=self.request.GET.get('type'))
        
        # Sorting by amount
        sort_direction = self.request.GET.get('sort_direction', 'desc')
        self.sort_direction_query_param = sort_direction
        query = query.order_by('amount' if sort_direction == 'asc' else '-amount')
        
        return query
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['sort_direction'] = 'desc' if self.sort_direction_query_param == 'asc' else 'asc'
        context['categories'] = Category.objects.all()
        context['types'] = [value for value, label in Transaction.TRANSACTION_TYPES]
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_type'] = self.request.GET.get('type', '')
        return context
    
    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.htmx:
            return render(self.request, "partials/transaction_table.html", context)
        return super().render_to_response(context, **response_kwargs)

class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "partials/transaction_table.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # To render the whole transaction tabel, paginated transactions are required  
        transactions = Transaction.objects.filter(user=self.request.user)
        paginator = Paginator(transactions, PAGINATION_SIZE)
        page_obj = paginator.get_page(1)
        # Merge the existing context dict with the new one
        context.update({
            "page_obj": page_obj,
            "paginator": paginator,
            "transactions": page_obj.object_list,
            "is_paginated": paginator.num_pages > 1,
            'categories': Category.objects.all(),
            'types': [value for value, label in Transaction.TRANSACTION_TYPES]
        })

        return context

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        messages.success(self.request, "Transaction added successfully!")
        if self.request.htmx:
            # htmx-oob is used to update multiple elements (table and messages) which are not in the same container  
            context['is_oob'] = True
            table_html = render_to_string("partials/transaction_table.html", context, request=self.request)
            message_html = render_to_string("components/messages.html", context, request=self.request)
            return HttpResponse(f"{table_html}{message_html}")

        return super().render_to_response(context)
 
class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "partials/transaction_row.html"
    
    def get_queryset(self):
        # Ensuring User can only update their own transactions
        return Transaction.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Transaction updated successfully!")
        return self.render_to_response(self.get_context_data())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['transaction'] = self.object
        return context
    
    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        
        if self.request.htmx:
            # htmx-oob is used to update multiple elements (table and messages) which are not in the same container  
            context['is_oob'] = True
            transaction_html = render_to_string("partials/transaction_row.html", context, request=self.request)
            message_html = render_to_string("components/messages.html", context, request=self.request)
            return HttpResponse(f"{transaction_html}{message_html}")
        return super().render_to_response(context, **response_kwargs)
     
class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = "partials/transaction_table.html"
    success_url = reverse_lazy('dashboard')
    
    def get_queryset(self):
        # Ensuring User can only update their own transactions
        return Transaction.objects.filter(user=self.request.user)
    
    # DeleteView doesn't utilize render_to_response like other views due to success_url, 
    # So, override the form_valid method where deletion occurs and change the return
    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        return self.render_to_response(self.get_context_data())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # To render the whole transaction tabel, paginated transactions are required  
        transactions = Transaction.objects.filter(user=self.request.user)
        paginator = Paginator(transactions, PAGINATION_SIZE)
        page_obj = paginator.get_page(1)
        # Merge the existing context dict with the new one
        context.update({
            "page_obj": page_obj,
            "paginator": paginator,
            "transactions": page_obj.object_list,
            "is_paginated": paginator.num_pages > 1,
            'categories': Category.objects.all(),
            'types': [value for value, label in Transaction.TRANSACTION_TYPES]
        })

        return context

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        messages.success(self.request, "Transaction deleted successfully!")
        if self.request.htmx:
            # htmx-oob is used to update multiple elements (table and messages) which are not in the same container  
            context['is_oob'] = True
            table_html = render_to_string("partials/transaction_table.html", context, request=self.request)
            message_html = render_to_string("components/messages.html", context, request=self.request)
            return HttpResponse(f"{table_html}{message_html}")

        return super().render_to_response(context)

def importcsv(request):
    if request.method == 'POST' and request.FILES.get("transaction_csv"):
        file = request.FILES["transaction_csv"]
        rows = csv.DictReader(TextIOWrapper(file, encoding='utf-8', newline=""))

        ### To make the 'keys' case-insensitive
        flattened_row = [] 
        for row in rows:
            row = {key.lower(): value for key, value in row.items()}
            flattened_row.append(row)
        
        rows = flattened_row

        count = 0 # To count transactions
        for row in rows:
            try:
                category = Category.objects.get(name__iexact=row['category'])
            except:
                category = Category.objects.create(name=row['category'])
            name = row['name']
            description = row['description']
            amount = row['amount']
            type = row['type']

            Transaction.objects.create(
                name=name,
                description=description,
                amount=amount,
                category=category,
                type=type,
                user = request.user,
            )

            count += 1
        return redirect('dashboard')

def exportcsv(request):
    filename = f"{request.user}-transactions-report-{datetime.today().strftime('%Y-%m-%d')}.csv"
    response = HttpResponse(
        content_type='text/csv',
        headers={
            "Content-Disposition":  f"attachment; filename={filename}"
            },
        )

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Description', 'Amount', 'Category', 'Type' ])
    for transaction in Transaction.objects.all():
        writer.writerow([
            transaction.id,
            transaction.name,
            transaction.description,
            transaction.amount,
            transaction.category,
            transaction.type,
        ])
    return response

def open_transaction_create_modal(request):
    form = TransactionForm()
    context = {
        'form': form,
        'transaction': None,  # Explicitly pass None for create
    }
    return render(request, "components/transaction_modal.html", context=context)

def open_transaction_update_modal(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)  # Ensure user owns the transaction
    form = TransactionForm(instance=transaction)
    context = {
        'form': form,
        'transaction': transaction,  # Pass the transaction for update
    }
    return render(request, "components/transaction_modal.html", context=context)
    
def close_modal(request):
    return render(request, "components/modal_placeholder.html")
    
@login_required
def reports_view(request):
    user = request.user
    
    # Get current date and set date range to last 6 months
    end_date = timezone.now()
    start_date = end_date - timedelta(days=180)
    
    transactions = Transaction.objects.filter(
        user=user,
        created_at__gte=start_date,
        created_at__lte=end_date
    )
    
    income_transactions = transactions.filter(type='income')
    income_amount = income_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    expense_transactions = transactions.filter(type='expense')
    expense_amount = expense_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    net_balance = income_amount - expense_amount
    avg_monthly_expense = expense_amount / 6 if expense_amount > 0 else 0  # Assuming 6 months by default
    
    # Format currency values
    formatted_income = f"${float(income_amount):,.2f}"
    formatted_expense = f"${float(expense_amount):,.2f}"
    formatted_net_balance = f"${float(net_balance):,.2f}"
    formatted_avg_monthly = f"${float(avg_monthly_expense):,.2f}"
    
    # Get expense by category
    expenses_by_category = []
    category_labels = []
    category_data = []
    category_colors = [
        "rgba(255, 99, 132, 0.9)",
        "rgba(54, 162, 235, 0.9)",
        "rgba(255, 206, 86, 0.9)",
        "rgba(75, 192, 192, 0.9)",
        "rgba(153, 102, 255, 0.9)",
        "rgba(255, 159, 64, 0.9)",
    ]
    category_borders = [
        "rgba(255, 99, 132, 1)",
        "rgba(54, 162, 235, 1)",
        "rgba(255, 206, 86, 1)",
        "rgba(75, 192, 192, 1)",
        "rgba(153, 102, 255, 1)",
        "rgba(255, 159, 64, 1)",
    ]
    
    # Get expenses by category
    expenses_by_category_query = transactions.filter(
        type='expense'
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    for item in expenses_by_category_query:
        expenses_by_category.append({
            'category__name': item['category__name'],
            'total': float(item['total'])
        })
    
    # Get monthly data for income vs expense trend
    months = []
    income_by_month = []
    expense_by_month = []
    
    # Get the last 6 months
    for i in range(5, -1, -1):
        month_date = end_date - timedelta(days=30 * i)
        month_name = month_date.strftime('%b')
        months.append(month_name)
        
        # Calculate month start and end dates
        month_start = datetime(month_date.year, month_date.month, 1, tzinfo=timezone.get_current_timezone())
        if month_date.month == 12:
            month_end = datetime(month_date.year + 1, 1, 1, tzinfo=timezone.get_current_timezone()) - timedelta(days=1)
        else:
            month_end = datetime(month_date.year, month_date.month + 1, 1, tzinfo=timezone.get_current_timezone()) - timedelta(days=1)
        
        # Get income for this month
        month_income = transactions.filter(
            type='income',
            created_at__gte=month_start,
            created_at__lte=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Get expenses for this month
        month_expense = transactions.filter(
            type='expense',
            created_at__gte=month_start,
            created_at__lte=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        income_by_month.append(float(month_income))
        expense_by_month.append(float(month_expense))
    
    # Get monthly breakdown by category
    categories = Category.objects.filter(
        transactions__user=user,
        transactions__type='expense'
    ).distinct()
    
    monthly_breakdown = []
    for category in categories:
        category_monthly_data = []
        for i in range(5, -1, -1):
            month_date = end_date - timedelta(days=30 * i)
            
            # Calculate month start and end dates
            month_start = datetime(month_date.year, month_date.month, 1, tzinfo=timezone.get_current_timezone())
            if month_date.month == 12:
                month_end = datetime(month_date.year + 1, 1, 1, tzinfo=timezone.get_current_timezone()) - timedelta(days=1)
            else:
                month_end = datetime(month_date.year, month_date.month + 1, 1, tzinfo=timezone.get_current_timezone()) - timedelta(days=1)
            
            # Get expenses for this category and month
            category_month_expense = transactions.filter(
                type='expense',
                category=category,
                created_at__gte=month_start,
                created_at__lte=month_end
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            category_monthly_data.append(float(category_month_expense))
        
        monthly_breakdown.append({
            'category': category.name,
            'data': category_monthly_data
        })
    
    # Process expenses by category for the chart
    if expenses_by_category_query:
        for item in expenses_by_category_query:
            category_labels.append(item['category__name'])
            category_data.append(float(item['total']))
    
    context = {
        'total_income': formatted_income,
        'total_expenses': formatted_expense,
        'net_balance': formatted_net_balance,
        'avg_monthly_expense': formatted_avg_monthly,
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'category_colors': json.dumps(category_colors),
        'category_borders': json.dumps(category_borders),
        'months': json.dumps(months),
        'income_by_month': json.dumps(income_by_month),
        'expense_by_month': json.dumps(expense_by_month),
        'monthly_breakdown': json.dumps(monthly_breakdown)
    }
    
    return render(request, 'transactions/reports.html', context)