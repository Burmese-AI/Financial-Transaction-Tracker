from django.urls import path
from .views import *

urlpatterns = [
    path("", TransactionListView.as_view(), name="dashboard"),
    path("transactions/", TransactionCreateView.as_view(), name="transaction_create"),
    path("transactions/<uuid:pk>/update", TransactionUpdateView.as_view(), name="transaction_update"),
    path("transactions/<uuid:pk>/delete", TransactionDeleteView.as_view(), name="transaction_delete"),
    path("transactions/modal/", open_transaction_create_modal, name="transaction_create_modal"),
    path("transactions/<uuid:pk>/modal/", open_transaction_update_modal, name="transaction_update_modal"),
    path("close-modal/", close_modal, name="close_modal"),
]