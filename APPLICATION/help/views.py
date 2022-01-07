from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from userapp.views import ContextProcessor


class HelpMain(LoginRequiredMixin, ContextProcessor, TemplateView):
    """Представление, формирующее страничку с справкой."""
    template_name = 'help/main.html'
