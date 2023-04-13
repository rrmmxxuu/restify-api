from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication

from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema

from ..accounts.models import User
from .models import Notification
from .serializers import NotificationCreateSerializer, NotificationGetSerializer

# Create your views here.

# noinspection PyTypeChecker
class NotificationCRView(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_summary="Create notification",
        operation_description="Create a notification that the sender is the authenticated user",
        request_body=NotificationCreateSerializer,
        responses={
            '201': "Notification sent successfully",
            '400': "Bad Request"
        }
    )
    def post(self, request):
        serializer = NotificationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['sender'] = self.request.user
            receiver = get_object_or_404(User.objects.filter(id=serializer.validated_data['receiver']))
            serializer.validated_data['receiver'] = receiver
            serializer.save()
            return Response("Notification sent successfully", status=201)
        return Response(status=400)

    @swagger_auto_schema(
        operation_summary="Get notification",
        operation_description="Get the notifications of the authenticated user.",
        responses={'200': NotificationGetSerializer}
    )
    def get(self, request):
        current_user = request.user.id
        notification_queryset = Notification.objects.filter(receiver_id=current_user, is_read=False)
        serializer = NotificationGetSerializer(instance=notification_queryset, many=True)
        return Response(serializer.data, status=200)


# noinspection PyTypeChecker
class NotificationIsReadView(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pk_url_kwarg = ('notification_id')

    @swagger_auto_schema(
        operation_summary="Set notification is read status",
        operation_description="Set the notification is read .",
        responses={'200': 'Set Is Read Successfully',
                   '403': 'Forbidden',
                   '404': 'Notification Not Found'}
    )
    def post(self, request, notification_id):
        notification_queryset = Notification.objects.filter(id=notification_id)
        notification = get_object_or_404(notification_queryset)
        if notification.receiver_id == request.user.id:
            notification_queryset.update(is_read=True)
            return Response("Set Is Read Successfully", status=200)
        return Response("Forbidden", status=403)



