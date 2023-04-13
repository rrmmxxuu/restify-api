from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Notification

class NotificationCreateSerializer(ModelSerializer):

    receiver = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = Notification
        fields = ('receiver', 'message')


class NotificationGetSerializer(ModelSerializer):

    class Meta:
        model = Notification
        fields = ('__all__')


