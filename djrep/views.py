from django.views.generic.edit import CreateView
from djrep.models import ReptileTraining
from djrep.forms import ReptileTrainingForm
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
import os
import base64
from djrep.reptile import ReptileParams


class DashboardView(LoginRequiredMixin, ListView):
    model = ReptileTraining
    template_name = "djrep/dashboard.html"
    context_object_name = "trainings"

    def get_queryset(self):
        return super().get_queryset()\
                        .filter(user=self.request.user).order_by('-id')


class NewRunView(LoginRequiredMixin, CreateView):
    model = ReptileTraining
    form_class = ReptileTrainingForm
    template_name = "djrep/new.html"
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RunView(LoginRequiredMixin, DetailView):
    model = ReptileTraining
    template_name = 'djrep/view.html'

    def get_queryset(self):
        return ReptileTraining.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        def _get_graph_base64_str(out_dir: str, out_file: str) -> str:
            graph_str = ''
            graph_path = ReptileTraining.get_base_save_path(self.object.id)\
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
