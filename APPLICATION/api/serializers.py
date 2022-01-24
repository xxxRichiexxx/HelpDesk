from rest_framework import serializers
from django.contrib.auth import get_user_model

from userapp.models import Request, Message, Service, Work

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
        )


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = '__all__'


class WorkSerializer(serializers.ModelSerializer):
    IDService = ServiceSerializer(many=False, read_only=True)

    class Meta:
        model = Work
        fields = '__all__'


class RequestViewSerializer(serializers.ModelSerializer):
    IDAutor = UserSerializer(read_only=True, many=False)
    IDExecutor = UserSerializer(read_only=True, many=False)
    IDResponsibilityGroup = serializers.SlugRelatedField(
        slug_field='Name',
        read_only=True,
        many=False,
    )
    IDWork = WorkSerializer(read_only=True, many=False)

    class Meta:
        model = Request
        fields = '__all__'
        read_only_fields = [
            'DateOfComplete',
            'Rating',
            'Status',
        ]


class RequestCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Request
        fields = ('Name', 'Сomment', 'IDWork')


class RequestChangeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Request
        fields = '__all__'
        read_only_fields = [
            'IDAutor',
        ]


class MessageViewOrCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = [
            'IDAutor',
            'IDRequest',
            'Status'
        ]


class MessageChangeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = [
            'IDAutor',
            'IDRequest'
        ]
