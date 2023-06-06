from django.urls import path
from djrep.views import DashboardView, NewRunView, RunView


urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('new', NewRunView.as_view(), name='new'),
    path('view/<int:pk>/', RunView.as_view(), name='view'),
]
