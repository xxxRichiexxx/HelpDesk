from django.urls import path

from .views import Analytics

app_name = 'analytics'

urlpatterns = [
    path('', Analytics.as_view(), name='all'),
]
