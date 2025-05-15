import json
from datetime import timedelta, datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import Transaction, Category

# Create your views here.

def transactions(request):
    return render(request, 'transactions/transactions.html')

def transactions_view(request):
    return render(request, 'transactions/transactions.html')

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

def test_htmx(request):
    try:
        return HttpResponse("<div class='text-green-600 font-semibold'>✅ HTMX is working! This response was loaded via AJAX.</div>")
    except Exception as e:
        return HttpResponse(f"<div class='text-red-600 font-semibold'>❌ Error: {str(e)}</div>")

