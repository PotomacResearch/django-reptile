import os
import base64

from django.views.generic.edit import CreateView
from djrep.models import Reptile, Dataset
from djrep.forms import ReptileCreateForm, DatasetCreateForm
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from djrep.reptile import ReptileParams
from django.http.response import FileResponse, Http404
from django.views.generic.base import View
from django.core.exceptions import ObjectDoesNotExist


class DashboardView(LoginRequiredMixin, ListView):
    model = Reptile
    template_name = "djrep/dashboard.html"
    context_object_name = "reptiles"

    def get_queryset(self):
        return super().get_queryset().filter(
                            user__account=self.request.user.account
                        ).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dataset_count'] = Dataset.objects.filter(
                                    user__account=self.request.user.account
                                                        ).count()
        return context


class NewDatasetView(LoginRequiredMixin, CreateView):
    model = Dataset
    form_class = DatasetCreateForm
    template_name = "djrep/dataset_new.html"
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class DatasetOverviewView(LoginRequiredMixin, ListView):
    model = Dataset
    template_name = "djrep/view_dataset.html"
    context_object_name = "datasets"

    def get_queryset(self):
        return super().get_queryset().filter(
                            user__account=self.request.user.account
                        ).order_by('-id')


class DatasetView(LoginRequiredMixin, DetailView):
    model = Dataset
    template_name = 'djrep/dataset_view.html'
    context_object_name = "dataset"

    def get_queryset(self):
        return super().get_queryset().filter(
                                    user__account=self.request.user.account)


class DatasetFileDownloadview(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            dataset = Dataset.objects.filter(
                            user__account=self.request.user.account
                                            ).get(id=kwargs['pk'])
            file_path = dataset.get_source_csv_path()
            return FileResponse(open(file_path, 'rb'),
                                content_type='application/octet-stream')
        except (FileNotFoundError, ObjectDoesNotExist):
            raise Http404('File not found.')


class NewReptileView(LoginRequiredMixin, CreateView):
    model = Reptile
    form_class = ReptileCreateForm
    template_name = "djrep/reptile_new.html"
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ReptileView(LoginRequiredMixin, DetailView):
    model = Reptile
    template_name = 'djrep/reptile_view.html'

    def get_queryset(self):
        return Reptile.objects.filter(user__account=self.request.user.account)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        def _get_graph_base64_str(out_dir: str, out_file: str) -> str:
            graph_str = ''
            graph_path = Reptile.get_base_save_path(self.object.id)\
                                                         / out_dir / out_file
            if os.path.exists(graph_path):
                with open(graph_path, 'rb') as i:
                    graph_str = base64.b64encode(i.read()).decode('utf-8')
            return graph_str

        context['esn_graph_image'] = _get_graph_base64_str(
                                        ReptileParams.esn_path, 'summary.png')
        context['autoencoder_graph_image'] = _get_graph_base64_str(
                                ReptileParams.autoencoder_path, 'summary.png')
        return context
