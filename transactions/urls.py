from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(views.transactions), name='transactions'),
    path('test-htmx/', views.test_htmx, name='test-htmx'),
]

