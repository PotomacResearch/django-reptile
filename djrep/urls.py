from django.urls import path
from djrep.views import DashboardView


urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]
