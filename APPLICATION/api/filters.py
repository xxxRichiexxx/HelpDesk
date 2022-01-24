import datetime as dt

import django_filters
from django.db.models import F, Q

from userapp.models import Request


class RequestFilter(django_filters.FilterSet):
    Status = django_filters.CharFilter(method='my_custom_filter')

    class Meta:
        model = Request
        fields = ['IDAutor__username', 'Status', 'IDResponsibilityGroup']

    def my_custom_filter(self, queryset, name, value):
        if value == 'lost':
            return queryset.filter(
                Q(Status='new') | Q(Status='in_work'),
                DateOfCreation__lt=dt.datetime.now() -
                F('IDWork__ReactionTime') -
                F('IDWork__TimeOfExecution')
            )
        return queryset.filter(**{
            name: value,
        })

