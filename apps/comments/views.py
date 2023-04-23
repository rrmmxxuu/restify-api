from django.http import HttpResponseBadRequest
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .models import Comments
from ..reservations.models import Reservation
from ..properties.models import Property
from .serializers import CommentSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404

# Create your views here.


# fetch all comments in one reservation
class CommentsDetails(APIView):
    permission_classes = (AllowAny,)
    pk_url_kwarg = 'reservation_id'
    @swagger_auto_schema(
        operation_summary="Get all comments for one reservation",
        operation_description="Get the comments details by the parameter reservation_id",
        security=[],
        manual_parameters=[openapi.Parameter('reservation_id',
                                             openapi.IN_PATH,
                                             description="Reservation ID you want to look up.",
                                             type=openapi.TYPE_STRING)],
        responses={
            '404': 'Reservation Not Found',
            '200': CommentSerializer
        }
    )
    def get(self, request, reservation_id):
        try:
            # Check if the reservation exists
            reservation = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            # Return a 404 response if the reservation does not exist
            return Response({'detail': 'Reservation not found.'}, status=404)
        # Get all comments for the given reservation
        comments = Comments.objects.filter(reservation=reservation_id)
        if not comments:
            # Return a 404 response if no comments are found
            return Response({'detail': 'Comments not found.'}, status=404)
        # Serialize the comments
        serializer = CommentSerializer(instance=comments, many=True)
        # Return the serialized comments
        return Response(serializer.data, status=200)


class CommentCreate(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    pk_url_kwarg = 'reservation_id'

    @swagger_auto_schema(
        operation_summary="Create a comment",
        operation_description="Create a comment for a specific reservation",
        request_body=CommentSerializer,
        responses={
            '200': CommentSerializer,
            '401': "Unauthorized"
        }
    )
    def post(self, request, reservation_id):
        # get the current user and reservation
        user = request.user
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Check if the reservation exists
                reservation = Reservation.objects.get(id=reservation_id)
            except Reservation.DoesNotExist:
                # Return a 404 response if the reservation does not exist
                return Response({'detail': 'Reservation not found.'}, status=404)
                # Check if the reservation status is "terminated" or "completed"
            if (reservation.status != 'Terminated') and (reservation.status != 'Completed'):
                return Response(
                    {'detail': 'Comments only for reservations that are terminated or completed.'},
                    status=400)
            if serializer.validated_data.get('parent_comment'):
                par_com_id = serializer.validated_data.get('parent_comment').id
                parent_comment = Comments.objects.get(id=par_com_id)
                if parent_comment.reservation.id != reservation_id:
                    return Response({'detail': 'Parent comment is not for the same reservation.'},
                                    status=400)
                else:
                    serializer.save(user=user, reservation=reservation)
                    return Response(serializer.data)
            else:
                # parent_comment is none, should check if the reservation has a start comment
                existing_comments = Comments.objects.filter(reservation=reservation_id, parent_comment=None)
                if existing_comments.exists():
                    return Response({'detail': 'A start comment already exists for this reservation.'},
                                    status=400)
                else:
                    serializer.save(user=user, reservation=reservation)
                    return Response(serializer.data)

        else:
            return Response(serializer.errors, status=400)


class CommentUD(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    pk_url_kwarg = 'comment_id'

    @swagger_auto_schema(
        operation_summary="Update specific comment",
        operation_description="Update the comment by the parameter comment_id",
        manual_parameters=[openapi.Parameter('comment_id',
                                             openapi.IN_PATH,
                                             description="Comment ID you want to modify.",
                                             type=openapi.TYPE_STRING),
                           ],
        request_body=CommentSerializer,
        responses={
            '401': 'Unauthorized',
            '404': 'Comment Not Found',
            '200': 'CommentSerializer'
        }
    )
    def patch(self, request, comment_id):
        try:
            comment = Comments.objects.get(id=comment_id)
        except Comments.DoesNotExist:
            return Response({'detail': 'Comment not found.'}, status=404)
        # if comment exist, update it
        serializer = CommentSerializer(instance=comment, data=request.data, partial=True)
        if serializer.is_valid():
            if request.user != comment.user:
                return Response("not allowed to modify others comment", status=401)
            serializer.save()
            return Response(serializer.data, status=200)

    @swagger_auto_schema(
        operation_summary="Delete specific comment",
        operation_description="Delete the comment by the parameter comment_id",
        manual_parameters=[openapi.Parameter('comment_id',
                                             openapi.IN_PATH,
                                             description="Comment ID you want to delete.",
                                             type=openapi.TYPE_STRING)],
        responses={
            '401': 'Unauthorized',
            '404': 'comment Not Found',
            '200': 'Deletion Successful'
        }
    )
    def delete(self, request, comment_id):
        user = request.user
        try:
            comment = Comments.objects.get(id=comment_id)
        except Comments.DoesNotExist:
            return Response({'detail': 'Comment not found.'}, status=404)
        # if comment exist, delete it
        comment.delete()
        return Response('Deletion successful', status=200)


class PropertyComments(APIView):
    permission_classes = (AllowAny,)
    pk_url_kwarg = 'property_id'

    @swagger_auto_schema(
        operation_summary="Get all comments for one property",
        operation_description="Get the comments details by the parameter property_id",
        security=[],
        manual_parameters=[openapi.Parameter('property_id',
                                             openapi.IN_PATH,
                                             description="Property ID you want to look up.",
                                             type=openapi.TYPE_STRING)],
        responses={
            '404': 'Property Not Found',
            '200': CommentSerializer
        }
    )
    def get(self, request, property_id):
        try:
            # Check if the property exists
            property_instance = Property.objects.get(property_id=property_id)
        except Property.DoesNotExist:
            # Return a 404 response if the property does not exist
            return Response({'detail': 'Property not found.'}, status=404)
        reservations = Reservation.objects.filter(property=property_id)
        comments = Comments.objects.filter(reservation__in=reservations)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class getOneComment(APIView):
    permission_classes = (AllowAny,)
    pk_url_kwarg = 'comment_id'

    def get(self, request, comment_id):
        try:
            # Check if the property exists
            comment = Comments.objects.get(id=comment_id)
        except Comments.DoesNotExist:
            # Return a 404 response if the property does not exist
            return Response({'detail': 'Comment not found.'}, status=404)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)






                



