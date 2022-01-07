from rest_framework.routers import SimpleRouter
from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url

from .views import RequestViewSet, MessageViewSet

router = SimpleRouter()
router.register('requests', RequestViewSet)
router.register(r'requests/(?P<request_id>\d+)/messages', MessageViewSet, basename='message')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include('djoser.urls')),
    path('v1/auth/', include('djoser.urls.jwt')),
    path('v1/auth/', include('rest_framework.urls')),
    path('v1/auth/api-token-auth/', views.obtain_auth_token),
]

# Настраиваем автоматическую документацию для API
schema_view = get_schema_view(
   openapi.Info(
      title="HelpDesk API",
      default_version='v1',
      description="Документация для приложения HelpDesk",
      # terms_of_service="URL страницы с пользовательским соглашением",
      # contact=openapi.Contact(email="admin@kittygram.ru"),
      # license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Подключаем автоматическую документацию для API
urlpatterns += [
   url(r'^swagger(?P<format>\.json|\.yaml)$',
       schema_view.without_ui(cache_timeout=0), name='schema-json'),
   url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
       name='schema-swagger-ui'),
   url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
       name='schema-redoc'),
]
