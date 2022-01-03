import re
import datetime as dt

from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from userapp.views import ContextProcessor
from userapp.models import Request


class SearchView(LoginRequiredMixin, ContextProcessor, ListView):
    """Представление, формирующее поисковую выдачу."""
    template_name = 'search/search_result.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        search = self.request.GET.get('search')
        if re.findall(r'\d{2}.\d{2}.\d{4}', search):
            date = dt.datetime.strptime(search, "%d.%m.%Y").date()
            result = Request.objects.filter(DateOfCreation__contains=date)
        else:
            result = Request.objects.filter(
                Q(id__icontains=search) |
                Q(IDWork__Name__icontains=search) |
                Q(IDWork__IDService__Name__icontains=search) |
                Q(Сomment__icontains=search) |
                Q(Name__icontains=search) |
                Q(IDAutor__last_name__icontains=search) |
                Q(IDExecutor__last_name__icontains=search)
            )
        return result
