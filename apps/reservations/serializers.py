from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Reservation
from ..accounts.models import User


class ReservationSerializer(ModelSerializer):

    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = ['tenant']
