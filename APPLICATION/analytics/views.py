from django.utils import timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, F
from django.contrib.auth import get_user_model
from django.db.models.functions import TruncMonth
from django.db.models.functions import Concat
from django.db.models import Value as V
from django.views.generic import TemplateView

from userapp.models import Request
from userapp.views import ContextProcessor

User = get_user_model()


class Analytics(LoginRequiredMixin, ContextProcessor, TemplateView):
    """Представление, формирующее страничку с аналитикой."""
    template_name = 'analytics/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Берем месяц для отчетности из параметров запроса или используем текущий месяц
        context['current_month'] = self.request.GET.get('month')
        if not context['current_month']:
            context['current_month'] = timezone.now().month
        # Формируем таблицу с пользователями и количеством отработанных ими заявок
        context['requests_per_users'] = Request.objects.filter(
            DateOfCreation__month=context['current_month']
            ).annotate(fullname=Concat(
                'IDExecutor__first_name', V(' '), 'IDExecutor__last_name'
                )
                ).values('fullname').annotate(
                    requests_count=Count('id'),
                    completed_requests=Count(
                        'id',
                        filter=Q(Status='completed')
                        ),
                    in_work_requests=Count(
                        'id',
                        filter=Q(Status='in_work')
                        ),
                    on_check_requests=Count(
                        'id',
                        filter=Q(Status='on_check')
                        ),
                    lost_requests=Count(
                        'id',
                        filter=Q(
                            DateOfCreation__lt=timezone.now() - F('IDWork__ReactionTime') - F('IDWork__TimeOfExecution'),
                            Status__in=['new', 'in_work']) |
                        Q(DateOfCreation__lt=F('DateOfComplete') - F('IDWork__ReactionTime') - F('IDWork__TimeOfExecution'),
                            Status='completed')
                        )
                    ).order_by()
        # Формируем перечень месяцев, который далее будем использовать для навигации по отчетности
        context['months'] = Request.objects.annotate(
            month=TruncMonth('DateOfCreation')
            ).values('month').annotate(count=Count('month')).order_by()
        # Формируем таблицу с количеством заявок по разным статусам
        context['requests'] = dict(Request.objects.filter(
            DateOfCreation__month=context['current_month']
            ).values_list('Status').annotate(count=Count('Status')).order_by())
        # Общее количество заявок за выбранный месяц
        context['all_requests_count'] = Request.objects.filter(
            DateOfCreation__month=context['current_month']
            ).values('Status').count()
        # Количество просроченных заявок
        context['lost_requests'] = Request.objects.filter(
            DateOfCreation__month=context['current_month']
            ).filter(
                Q(DateOfCreation__lt=timezone.now() - F('IDWork__ReactionTime') - F('IDWork__TimeOfExecution'),
                    Status__in=['new', 'in_work']) |
                Q(DateOfCreation__lt=F('DateOfComplete') - F('IDWork__ReactionTime') - F('IDWork__TimeOfExecution'),
                    Status='completed')
                ).count()
        return context
