from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from userapp.views import Index

urlpatterns = [
    path('', Index.as_view()),    
    path('registration/', include('registration.urls', namespace='registration')),
    path('authentication/', include('authentication.urls', namespace='authentication')),
    path('authentication/', include('django.contrib.auth.urls')),
    path('user-app/', include('userapp.urls', namespace='user-app')),
    path('admin/', admin.site.urls),    
]



if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT) 