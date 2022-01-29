from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404

from userapp.models import Request, ResponsibilityGroup, Message, Service
from .serializers import (RequestViewSerializer,
                          RequestCreateOrChangeSerializer,
                          RequestUpdateSerializer,
                          MessageViewOrCreateSerializer,
                          MessageChangeSerializer,
                          ServiceSerializer,
                          RequestSetRatingSerializer)
from .permissions import AuthorPermission, SetRatingPermission
from .filters import RequestFilter


class RequestViewSet(viewsets.ModelViewSet):
    """
    Реализует следующий функционал:
    1) Список заявок(обращений) - доступно всем
    2) Детализацию по выбранной заявке - доступно всем
    3) Создание заявки - доступно аутентифицированным
    4) Редактирование заявки - доступно автору или сотруднику service desk
    6) Удаление заявки - доступно автору или сотруднику service desk
    7) Пагинация вида api/v1/requests/?limit=3&offset=5
    8) Фильтрация вида api/v1/requests/?IDAuthor__username=andrey&Status=new
    9) Поиск вида api/v1/requests/?search=тест
    """
    queryset = Request.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_class = RequestFilter
    search_fields = (
        'IDWork__Name', 'IDWork__IDService__Name',
        'DateOfCreation',
        'Name', 'Сomment',
        'IDAuthor__first_name', 'IDAuthor__last_name',
        'IDExecutor__first_name', 'IDExecutor__last_name',
        'IDResponsibilityGroup__Name',
    )

    def perform_create(self, serializer):
        id_responsibility_group = ResponsibilityGroup.objects.get(Default=True)
        serializer.save(
            IDAuthor=self.request.user,
            IDResponsibilityGroup=id_responsibility_group
        )

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return RequestUpdateSerializer
        elif self.action in ('create', 'update'):
            return RequestCreateOrChangeSerializer
        return RequestViewSerializer


class SetRatingViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Данное представление позволяет авторам оценивать работу по заявке.
    """
    queryset = Request.objects.all()
    serializer_class = RequestSetRatingSerializer
    permission_classes = (SetRatingPermission,)


class MessageViewSet(viewsets.ModelViewSet):
    """
    Реализует следующий функционал:
    1) Список сообщений по выбранной заявке - доступно всем
    2) Детализацию по конкретному сообщению - доступно всем
    3) Создание сообщения - доступно аутентифицированным
    4) Редактирование сообщения - доступно автору
    5) Удаление сообщения - доступно автору
    """
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = (
        'IDRequest', 'Date', 'IDAuthor',
        'IDRecipient', 'Status',
    )
    search_fields = ('Text',)

    def get_queryset(self):
        request_id = self.kwargs.get('request_id')
        return Message.objects.filter(IDRequest=request_id)

    def perform_create(self, serializer):
        request = get_object_or_404(Request, id=self.kwargs.get('request_id'))
        serializer.save(
            IDAuthor=self.request.user,
            IDRequest=request
        )

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return MessageChangeSerializer
        return MessageViewOrCreateSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Реализует следующий функционал:
    1) Список сервисов - доступно аутентифицированным
    2) Детализацию по конкретному сервису - доступно аутентифицированным
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
