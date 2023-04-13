from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework_simplejwt import authentication

from django.shortcuts import get_object_or_404

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import UserProfile
from .serializers import UserSerializer, UserRegisterSerializer, UserChangePasswordSerializer, UserProfileSerializer

import time
# Create your views here.

# noinspection PyTypeChecker
class UserDetailView(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        operation_summary="Get the user's basic info",
        operation_description="Get the logged in user's basic information.",
        responses={
        '200': UserSerializer,
        '401': "Unauthorized"
        }
    )
    def get(self, request):
        current_user = request.user
        serializer = UserSerializer(instance=current_user, many=False)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update the user's basic info",
        operation_description="Update the logged in user's basic information. \n"
                              " All fields are required. \n"
                              "Existed email addresses are not allowed and will be checked by the backend.",
        request_body=UserSerializer,
        responses={
            '200': UserSerializer,
            '400': 'Email: This field must be unique',
            '401': 'Unauthorized'
        }
    )
    def put(self, request):
        current_user = request.user
        data = request.data
        serializer = UserSerializer(instance=current_user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class UserRegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny, )
    serializer_class = UserRegisterSerializer

    response_schema_dict = {
        "200": openapi.Response(
            description="Success"
        ),
        "400": openapi.Response(
            description="The user already exists",
        )
    }
    @swagger_auto_schema(
        operation_summary="User register",
        operation_description="Register the user to the database.",
        security=[],
        responses=response_schema_dict
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class UserChangePasswordView(APIView):
    authentication_classes = (authentication.JWTAuthentication, )
    permission_classes = (IsAuthenticated, )

    response_schema_dict = {
        "200": openapi.Response(
            description="Success"
        ),
        "400": openapi.Response(
            description="Bad Requests",
            examples={
                "application/json": {
                    "old_password": "Incorrect old password",
                    "new_password": "Cannot be the same as your old password",
                }
            }
        ),
        "401": openapi.Response(
            description="User is not authenticated",
        )
    }

    @swagger_auto_schema(
        operation_summary="Change password",
        operation_description="Change the password of the current user.",
        request_body=UserChangePasswordSerializer,
        responses=response_schema_dict
    )
    def put(self, request):
        current_user = request.user
        data = request.data
        serializer = UserChangePasswordSerializer(instance=current_user, data=data, context=current_user)

        if serializer.is_valid():
            serializer.update(instance=current_user, validated_data=serializer.validated_data)
            return Response({"Success"}, status=200)

        return Response(serializer.errors, status=400)


class UserProfileView(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        operation_summary="Get the user's profile",
        operation_description="Get the current user's profile data.",
        responses={
            '200': UserProfileSerializer,
            '401': "Unauthorized"
        }
    )
    def get(self, request):
        current_user_id = request.user.id
        profile = get_object_or_404(UserProfile.objects.filter(user_id=current_user_id))
        serializer = UserProfileSerializer(instance=profile, many=False, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create user profile",
        operation_description="Initialize user profile for the current user",
        request_body=UserProfileSerializer,
        responses={
            '201': UserSerializer,
            '401': "Unauthorized"
        }
    )
    def post(self, request):
        current_user = request.user
        data = request.data
        serializer = UserProfileSerializer(data=data, context=current_user)
        if serializer.is_valid():
            serializer.create(validated_data=serializer.validated_data)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_summary="Update user profile",
        operation_description="Update user profile for the current user",
        request_body=UserProfileSerializer,
        responses={
            '200': UserSerializer,
            '401': "Unauthorized"
        }
    )
    def patch(self, request):
        current_user_profile = UserProfile.objects.get(user_id=request.user)
        data = request.data
        serializer = UserProfileSerializer(instance=current_user_profile, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)


