import datetime as dt

from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, F, Avg
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
        # Формируем перечень месяцев, который далее будем использовать для навигации по отчетности
        context['months'] = Request.objects.annotate(
            month=TruncMonth('DateOfCreation')
            ).values('month').annotate(count=Count('month')).order_by()

        # Берем месяц для отчетности из параметров запроса или используем текущий месяц
        month = self.request.GET.get('month')
        if not month:
            context['current_month'] = timezone.now()
        else:
            context['current_month'] = dt.datetime.strptime(month, "%Y-%m")

        # Формируем таблицу с пользователями и количеством отработанных ими заявок
        context['requests_per_users'] = Request.objects.filter(
            DateOfCreation__month=context['current_month'].month,
            DateOfCreation__year=context['current_month'].year
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
                            DateOfCreation__lt=timezone.now() -
                            F('IDWork__ReactionTime') -
                            F('IDWork__TimeOfExecution'),
                            Status__in=['new', 'in_work']) |
                        Q(DateOfCreation__lt=F('DateOfComplete') -
                            F('IDWork__ReactionTime') -
                            F('IDWork__TimeOfExecution'),
                            Status='completed')
                        )
                    ).order_by()

        # Формируем таблицу с количеством заявок по разным статусам
        # (для построения графика)
        context['requests'] = dict(
            Request.objects.filter(
                DateOfCreation__month=context['current_month'].month,
                DateOfCreation__year=context['current_month'].year
            ).values_list('Status').annotate(count=Count('Status')).order_by()
        )
        # Количество просроченных заявок
        lost_requests = Request.objects.filter(
            DateOfCreation__month=context['current_month'].month,
            DateOfCreation__year=context['current_month'].year
            ).filter(
                Q(DateOfCreation__lt=timezone.now() - F('IDWork__ReactionTime') - F('IDWork__TimeOfExecution'),
                    Status__in=['new', 'in_work']) |
                Q(DateOfCreation__lt=F('DateOfComplete') - F('IDWork__ReactionTime') - F('IDWork__TimeOfExecution'),
                    Status='completed')
                ).count()
        context['requests']['lost_requests'] = lost_requests

        # Общее количество заявок за выбранный месяц
        context['all_requests_count'] = Request.objects.filter(
            DateOfCreation__month=context['current_month'].month,
            DateOfCreation__year=context['current_month'].year
            ).values('Status').count()

        # Среднее время выполнения заявки
        context['average_execution_time'] = round(
            Request.objects.filter(
                Status='completed',
                DateOfCreation__month=context['current_month'].month,
                DateOfCreation__year=context['current_month'].year
            ).annotate(
                execution_time=F('DateOfComplete') - F('DateOfCreation')
            ).aggregate(Avg('execution_time'))['execution_time__avg'].total_seconds()/60,
            0)

        # Доля просроченных заявок
        context['lost_requests_percent'] = round(lost_requests/context['all_requests_count']*100, 0)
        return context
