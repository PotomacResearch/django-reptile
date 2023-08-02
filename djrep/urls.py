from django.urls import path
from djrep.views import DashboardView, NewReptileView, ReptileView,\
    NewDatasetView, DatasetOverviewView, DatasetView, DatasetFileDownloadview


urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('newreptile', NewReptileView.as_view(), name='newreptile'),
    path('newdataset', NewDatasetView.as_view(), name='newdataset'),
    path('datasets', DatasetOverviewView.as_view(), name='datasets'),
    path('reptileview/<int:pk>/', ReptileView.as_view(), name='reptileview'),
    path('datasetview/<int:pk>/', DatasetView.as_view(), name='datasetview'),
    path('datasetdownload/<int:pk>', DatasetFileDownloadview.as_view(),
                                     name='datasetdownload')
]
