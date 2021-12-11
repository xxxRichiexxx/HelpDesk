from django.contrib.auth import views
from django.urls import path

app_name = 'authentication'

urlpatterns = [
    path('login/',
         views.LoginView.as_view(template_name='authentication/login.html'),
         name="login"),
    path('logout/',
         views.LogoutView.as_view(template_name='authentication/logout.html'),
         name="logout"),
]
