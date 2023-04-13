from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Reservation


class ReservationSerializer(ModelSerializer):
    class Meta:
        model = Reservation
        fields = "__all__"
