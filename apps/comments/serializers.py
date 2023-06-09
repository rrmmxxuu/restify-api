from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Comments


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comments
        fields = "__all__"
        read_only_fields = ('user',)

