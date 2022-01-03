from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from userapp.views import ContextProcessor


class Index(LoginRequiredMixin, ContextProcessor, TemplateView):
    """Отображает стартовую страницу."""
    template_name = 'index/index.html'
