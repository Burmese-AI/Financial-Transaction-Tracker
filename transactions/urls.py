from django.urls import path
from .views import *

urlpatterns = [
    ### Class-based Views 
    path("", TransactionListView.as_view(), name="dashboard"),
    path("transactions/", TransactionCreateView.as_view(), name="transaction_create"),
    path("transactions/<uuid:pk>/update", TransactionUpdateView.as_view(), name="transaction_update"),
    path("transactions/<uuid:pk>/delete", TransactionDeleteView.as_view(), name="transaction_delete"),
    path("transactions/search", TransactionSearchView.as_view(), name="transaction_search"),
    path("transactions/sort", TransactionSortView.as_view(), name="transaction_sort"), 
    path("transactions/Filter", TransactionFilterView.as_view(), name="transaction_filter"),

    ### Function Views
    path("transactions/modal/", open_transaction_create_modal, name="transaction_create_modal"),
    path("transactions/<uuid:pk>/modal/", open_transaction_update_modal, name="transaction_update_modal"),
    path("close-modal/", close_modal, name="close_modal"),
]