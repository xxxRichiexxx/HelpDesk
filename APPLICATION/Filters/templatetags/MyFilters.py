from django import template
from django.db.models.aggregates import Count
from userapp.models import Request

register = template.Library()


def Requests_Count(value):
    count = Request.objects.filter(
        IDWork__IDService__id=value.id, Status="Новая"
        ).aggregate(Count('id'))['id__count']
    return count


def Len(value):
    return len(value)


register.filter('Len', Len)
register.filter('Requests_Count', Requests_Count)


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})
