from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404

from userapp.models import Request, ResponsibilityGroup, Message
from .serializers import (RequestViewOrCreateSerializer,
                          RequestChangeSerializer,
                          MessageViewOrCreateSerializer,
                          MessageChangeSerializer)
from .permissions import AuthorPermission


class RequestViewSet(viewsets.ModelViewSet):
    """
    Реализует следующий функционал:
    1) Список заявок(обращений) - доступно всем
    2) Детализацию по выбранной заявке - доступно всем
    3) Создание заявки - доступно аутентифицированным
    4) Редактирование заявки - доступно автору
    5) Удаление заявки - доступно автору
    """
    queryset = Request.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = '__all__'
    search_fields = ('Сomment', 'Name', )

    def perform_create(self, serializer):
        id_responsibility_group = ResponsibilityGroup.objects.get(Default=True)
        serializer.save(
            IDAutor=self.request.user,
            IDResponsibilityGroup=id_responsibility_group
        )

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return RequestChangeSerializer
        return RequestViewOrCreateSerializer


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
        'IDRequest', 'Date', 'IDAutor',
        'IDRecipient', 'Status',
    )
    search_fields = ('Text',)

    def get_queryset(self):
        request_id = self.kwargs.get('request_id')
        return Message.objects.filter(IDRequest=request_id)

    def perform_create(self, serializer):
        request = get_object_or_404(Request, id=self.kwargs.get('request_id'))
        serializer.save(
            IDAutor=self.request.user,
            IDRequest=request
        )

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return MessageChangeSerializer
        return MessageViewOrCreateSerializer