from rest_framework.routers import SimpleRouter
from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url

from .views import RequestViewSet, MessageViewSet, ServiceViewSet, SetRatingViewSet

router_v1 = SimpleRouter()
router_v1.register('requests', RequestViewSet)
router_v1.register(r'requests/(?P<request_id>\d+)/messages', MessageViewSet, basename='message')
router_v1.register('services', ServiceViewSet)
router_v1.register('requests/set-rating', SetRatingViewSet)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include('djoser.urls')),  # аутентификация jwt. работа с пользователями
    path('v1/auth/', include('djoser.urls.jwt')),  # аутентификация jwt. работа с токенами
    path('v1/auth/', include('rest_framework.urls')),  # ссылки на логин/логаут при работе с api через web.
    path('v1/auth/api-token-auth/', views.obtain_auth_token),  # аутентификация токеном.
]

# Настраиваем автоматическую документацию для API
schema_view = get_schema_view(
   openapi.Info(
       title="HelpDesk API",
       default_version='v1',
       description="Документация для приложения HelpDesk",
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
