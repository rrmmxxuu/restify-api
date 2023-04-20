from django.db.models import Q
from rest_framework.response import Response
from .models import Reservation
from ..properties.models import Property
from .serializers import ReservationSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


# Create your views here.

class ReservationsView(APIView):
    permission_classes = (AllowAny,)
    pk_url_kwarg = 'property_id'

    @swagger_auto_schema(
        operation_summary="Get all reservations for one property",
        operation_description="Get reservations by the parameter property_id",
        security=[],
        manual_parameters=[openapi.Parameter('property_id',
                                             openapi.IN_PATH,
                                             description="Property ID you want to look up.",
                                             type=openapi.TYPE_STRING)],
        responses={
            '404': 'Property or reservations Not Found',
            '200': ReservationSerializer
        }
    )
    def get(self, request, property_id):
        try:
            # Check if the reservation exists
            property_instance = Property.objects.get(property_id=property_id)
        except Property.DoesNotExist:
            # Return a 404 response if the reservation does not exist
            return Response({'detail': 'Property not found.'}, status=404)
        # Get all reservations for the given property
        reservations = Reservation.objects.filter(property=property_id)
        if not reservations:
            # Return a 404 response if no comments are found
            return Response({'detail': 'reservations not found.'}, status=404)
        # Serialize the comments
        serializer = ReservationSerializer(instance=reservations, many=True)
        # Return the serialized comments
        return Response(serializer.data, status=200)


class ReservationCreate(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pk_url_kwarg = 'property_id'

    @swagger_auto_schema(
        operation_summary="Create a reservation",
        operation_description="Create a reservation for a specific property",
        request_body=ReservationSerializer,
        responses={
            '200': ReservationSerializer,
            '401': "Unauthorized",
            '400': "bad request e.g:There is a conflicting reservation for the this property."
        }
    )
    def post(self, request, property_id):
        tenant = request.user
        property_obj = get_object_or_404(Property, property_id=property_id)
        # Create a serializer with the request data
        serializer = ReservationSerializer(data=request.data)
        reservations = Reservation.objects.filter(property=property_id)
        # if property exists, check if there is any reservations conflict to this one
        if reservations:
            if serializer.is_valid():
                # Get the validated start_date and end_date
                start_date = serializer.validated_data.get('start_date')
                end_date = serializer.validated_data.get('end_date')
                status = serializer.validated_data.get('status')
                if status != 'Pending':
                    return Response({'detail': 'Status should be pending when create reservation'},
                                    status=400)
                # Check if there are any conflicting reservations for the same property
                conflicting_reservations = Reservation.objects.filter(
                    Q(property=property_id) &
                    (Q(status='Approved') | Q(status='Pending')) &
                    ((Q(start_date__range=[start_date, end_date]) |
                      Q(end_date__range=[start_date, end_date])) |
                     (Q(start_date__lte=start_date) & Q(end_date__gte=end_date)))
                )
                if conflicting_reservations.exists():
                    return Response({'detail': 'There is a conflicting reservation for the this property.'},
                                    status=400)

                serializer.save(tenant=tenant)
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=400)
        else:
            if serializer.is_valid():
                serializer.save(tenant=tenant)
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=400)


class ReservationUD(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pk_url_kwarg = 'reservation_id'

    @swagger_auto_schema(
        operation_summary="Update specific reservation",
        operation_description="Update the reservation by the parameter reservation_id",
        manual_parameters=[openapi.Parameter('reservation_id',
                                             openapi.IN_PATH,
                                             description="Reservation ID you want to modify.",
                                             type=openapi.TYPE_STRING),
                           ],
        request_body=ReservationSerializer,
        responses={
            '401': 'Unauthorized',
            '404': 'Reservation Not Found',
            '200': ReservationSerializer,
            '400': 'Bad request, e.g: modified date conflicts with another reservation'
        }
    )
    def put(self, request, reservation_id):
        tenant = request.user
        try:
            reservation = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            return Response({'detail': 'reservation not found.'}, status=404)
        # if reservation exist, update it
        serializer = ReservationSerializer(instance=reservation, data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            property_id = serializer.validated_data.get('property')
            # Check if there are any conflicting reservations for the same property
            conflicting_reservations = Reservation.objects.filter(
                Q(property=property_id) &
                (Q(status='Approved') | Q(status='Pending')) &
                ((Q(start_date__range=[start_date, end_date]) |
                  Q(end_date__range=[start_date, end_date])) |
                 (Q(start_date__lte=start_date) & Q(end_date__gte=end_date)))
            ).exclude(id=reservation_id)

            if conflicting_reservations.exists():
                return Response({'detail': 'There is a conflicting reservation for the this property.'},
                                status=400)
            serializer.save(tenant=tenant)
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors)

    @swagger_auto_schema(
        operation_summary="Delete specific reservation",
        operation_description="Delete the reservation by the parameter reservation_id",
        manual_parameters=[openapi.Parameter('reservation_id',
                                             openapi.IN_PATH,
                                             description="Reservation ID you want to delete.",
                                             type=openapi.TYPE_STRING)],
        responses={
            '401': 'Unauthorized',
            '404': 'Reservation Not Found',
            '200': 'Deletion Successful'
        }
    )
    def delete(self, request, reservation_id):
        tenant = request.user
        try:
            comment = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            return Response({'detail': 'reservation not found.'}, status=404)
        # if comment exist, delete it
        comment.delete()
        return Response('Deletion successful', status=200)


class ReservationGetMyView(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tenant = request.user
        reservation_queryset = Reservation.objects.filter(tenant=tenant)
        serializer = ReservationSerializer(instance=reservation_queryset, many=True, context={'request': request})
        return Response(serializer.data, status=200)

