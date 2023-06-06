from django.views.generic.edit import CreateView
from djrep.models import ReptileTraining
from djrep.forms import ReptileTrainingForm
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView


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
