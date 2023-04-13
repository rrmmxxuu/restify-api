from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator
from django.conf import settings
from urllib.parse import urljoin

from .models import User, UserProfile


class UserSerializer(ModelSerializer):
    """
    Serializer for model User
    """

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True
    )
    first_name = serializers.CharField(
        max_length=150,
        required=True
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True
    )


class UserRegisterSerializer(ModelSerializer):
    """
    Serializer specifically used to hanlde registration
    """

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(
        max_length=150,
        required=True
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True
    )
    password = serializers.CharField(
        required=True,
        write_only=True
    )

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserChangePasswordSerializer(ModelSerializer):
    """
    Serializer specifically for changing password
    """

    class Meta:
        model = User
        fields = ['old_password', 'new_password']

    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Incorrect old password"})
        return value

    def validate_new_password(self, value):
        user = self.context
        if user.check_password(value):
            raise serializers.ValidationError({"new_password": "Cannot be the same as your old password"})

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for model UserProfile
    """

    class Meta:
        model = UserProfile
        fields = ['user_id', 'phone', 'date_of_birth', 'avatar', 'gender', 'rating']

    user_id = serializers.CharField(max_length=150, required=False, read_only=True)
    phone = serializers.CharField(max_length=10, required=False)
    date_of_birth = serializers.DateField(required=False)
    avatar = serializers.ImageField(required=False)
    gender = serializers.CharField(required=False)
    rating = serializers.DecimalField(decimal_places=1, max_digits=2, required=False)

    def create(self, validated_data):
        user = self.context
        validated_data['user_id'] = user.id
        user_profile = UserProfile.objects.create(**validated_data)
        return user_profile

    def update(self, instance, validated_data):
        instance.phone = validated_data.get('phone', instance.phone)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.save()
        return instance

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            else:
                return obj.avatar.url
        return None
