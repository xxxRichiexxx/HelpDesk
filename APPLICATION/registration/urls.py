from django.urls import path
from registration import views

app_name = 'registration'

urlpatterns = [
    path('', views.registration, name='reg-form'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
