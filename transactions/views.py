from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, CreateView
from django.core.paginator import Paginator
from django.contrib import messages
from django.template.loader import render_to_string
from typing import Any
from .models import Transaction, Category, Budget
from .forms import TransactionCreateForm

PAGINATION_SIZE = 10

class TransactionListView(ListView):
    model = Transaction
    template_name = 'dashboard.html'
    context_object_name = 'transactions'
    paginate_by = PAGINATION_SIZE
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context
    
    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.htmx:
            return render(self.request, "partials/transaction_table.html", context)
        return super().render_to_response(context, **response_kwargs)

class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionCreateForm
    template_name = "partials/transaction_table.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        messages.success(self.request, "Transaction added successfully!")
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
        })

        return context

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        # Make sure overriden context dict is inlcuded for transactions
        if context is None: 
            context = self.get_context_data()

        if self.request.htmx:
            # htmx-oob is used to update multiple elements (table and messages) which are not in the same container  
            context['is_oob'] = True
            table_html = render_to_string("partials/transaction_table.html", context, request=self.request)
            message_html = render_to_string("components/messages.html", context, request=self.request)
            return HttpResponse(f"{table_html}{message_html}")

        return super().render_to_response(context)
   
def open_transaction_create_modal(request):
    form = TransactionCreateForm()
    context = {
        'form': form
    }
    return render(request, "components/transaction_create_modal.html", context=context)
    
def close_modal(request):
    return render(request, "components/modal_placeholder.html")
    
    