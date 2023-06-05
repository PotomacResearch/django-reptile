from django.urls import path
from djrep.views import DashboardView, NewRunView


urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('new', NewRunView.as_view(), name='new'),
]
