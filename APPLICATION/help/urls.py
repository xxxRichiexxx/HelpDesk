from django.urls import path

from .views import HelpMain

app_name = 'help'

urlpatterns = [
    path('',
         HelpMain.as_view(),
         name='main'),
 ]