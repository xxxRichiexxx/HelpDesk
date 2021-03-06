from django.urls import path

from userapp import views
from search.views import SearchView

app_name = 'user-app'

urlpatterns = [
    path('all-requests/search/',
         SearchView.as_view(),
         {'scope': 'all-requests',
          'filter': 'search'},
         name='search'),
    path('all-requests/<str:filter>/',
         views.AllRequests.as_view(),
         {'scope': 'all-requests'},
         name='allrequests'),
    path('<str:scope>/<str:filter>/',
         views.UserAPP.as_view(),
         name="requests"),
    path('<str:scope>/<str:filter>/<int:pk>/<str:type>/',
         views.RequestDetail.as_view(),
         name="details"),
    path('requests-by-category/',
         views.RequestsByCategory.as_view(),
         {'scope': 'category-list', 'filter': 'None'},
         name='requests-by-category'),
    path('request-creating/',
         views.CreateRequest.as_view(),
         name='request-creating'),
    path('request-creating2/', views.CreateRequest2.as_view()),
    path('set-rating/', views.set_rating, name='set-rating'),
    path('set-status/', views.set_status),
    path('escalation/', views.excalation),
    path('sendmessage/', views.send_message),
    path('clean-messages/', views.clean_messages),
]
