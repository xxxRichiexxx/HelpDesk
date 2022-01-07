from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from index.views import Index

urlpatterns = [
    path('', Index.as_view()),    
    path('registration/', include('registration.urls', namespace='registration')),
    path('authentication/', include('authentication.urls', namespace='authentication')),
    path('authentication/', include('django.contrib.auth.urls')),
    path('user-app/', include('userapp.urls', namespace='user-app')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('help/', include('help.urls', namespace='help')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),    
]



if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT) 