from django.urls import path
from djrep.views import DashboardView, NewReptileView, ReptileView,\
    NewDatasetView


urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('newreptile', NewReptileView.as_view(), name='newreptile'),
    path('newdataset', NewDatasetView.as_view(), name='newdataset'),
    path('view/<int:pk>/', ReptileView.as_view(), name='view'),
]
