from django import template
from django.db.models.aggregates import Count
from django.db.models import Q

from userapp.models import Request

register = template.Library()


# Фильтр устарел и не используется. Оставлен тут в учебных целях.
def Requests_Count(value):
    count = Request.objects.filter(
        Q(Status="new")|Q(Status="in_work"), IDWork__IDService__id=value.id
        ).aggregate(Count('id'))['id__count']
    return count


def Len(value):
    return len(value)


register.filter('Len', Len)
register.filter('Requests_Count', Requests_Count)


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})

