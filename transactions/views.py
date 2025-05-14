from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.

def transactions(request):
    return render(request, 'transactions/transactions.html')

def transactions_view(request):
    return render(request, 'transactions/transactions.html')

def test_htmx(request):
    try:
        return HttpResponse("<div class='text-green-600 font-semibold'>✅ HTMX is working! This response was loaded via AJAX.</div>")
    except Exception as e:
        return HttpResponse(f"<div class='text-red-600 font-semibold'>❌ Error: {str(e)}</div>")
