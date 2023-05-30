from django.views.generic.base import TemplateView


class DashboardView(TemplateView):
    template_name = "djrep/dashboard.html"
