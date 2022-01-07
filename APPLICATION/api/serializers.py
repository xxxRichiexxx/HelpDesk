from rest_framework import serializers
from userapp.models import Request, Message


class RequestViewOrCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Request
        fields = '__all__'
        read_only_fields = [
            'IDAutor',
            'IDResponsibilityGroup',
            'IDExecutor',
            'DateOfComplete',
            'Rating',
            'Status',
        ]


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
