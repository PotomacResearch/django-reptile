from django.urls import path
from djrep.views import DashboardView, NewRunView, RunView, params_view


urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('new', NewRunView.as_view(), name='new'),
    path('view/<int:pk>/', RunView.as_view(), name='view'),
    path('params', params_view, name='params')
]
