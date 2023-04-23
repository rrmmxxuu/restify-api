from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination

from rest_framework_simplejwt import authentication

from django.db.models import Q, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import datetime

from .models import Property, PropertyImage
from ..reservations.models import Reservation
from .serializers import PropertySerializer, PropertyImageSerializer

# Create your views here.

class PropertyDetailsView(APIView):
    permission_classes = (AllowAny,)
    pk_url_kwarg = 'property_id'
    @swagger_auto_schema(
        operation_summary="Get specific property details",
        operation_description="Get the property details by the parameter property_id",
        security=[],
        manual_parameters=[openapi.Parameter('property_id',
                                             openapi.IN_PATH,
                                             description="Property ID you want to look up.",
                                             type=openapi.TYPE_STRING)],
        responses={
            '404': 'Property Not Found',
            '200': PropertySerializer
        }
    )
    def get(self, request, property_id):
        queryset = Property.objects.filter(property_id=property_id)
        property = get_object_or_404(queryset)
        serializer = PropertySerializer(instance=property, many=False)

        return Response(serializer.data, status=200)


class PropertyCreateView(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        operation_summary="Create property",
        operation_description="Create a property under the current user.",
        request_body=PropertySerializer,
        responses={
            '201': PropertySerializer,
            '401': "Unauthorized"
        }
    )
    def post(self, request):
        owner = request.user
        data = request.data
        serializer = PropertySerializer(data=data)
        if serializer.is_valid():
            created_property = serializer.save(owner=owner)
            property_id = created_property.property_id
            return Response({"message": "Created successfully", "property_id": property_id}, status=201)
        print(serializer.errors)
        return Response(serializer.errors, status=400)


class PropertyImageCreateView(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pk_url_kwarg = 'property_id'

    @swagger_auto_schema(
        operation_summary="Upload a property image",
        operation_description="Upload an image to the given property_id",
        request_body=PropertyImageSerializer,
        responses={
            '401': 'Unauthorized',
            '403': 'Forbidden',
            '404': 'Property Not Found',
            '201': 'Uploaded Successful',
        }
    )
    def post(self, request, property_id):
        owner = request.user
        data = request.data
        queryset = Property.objects.filter(property_id=property_id)
        property = get_object_or_404(queryset)
        if property.owner != owner:
            return Response('Forbidden', status=403)
        serializer = PropertyImageSerializer(data=data)
        if serializer.is_valid():
            serializer.save(property_id=property_id)
            return Response("Uploaded successfully", status=201)

        return Response(serializer.errors, status=400)


class PropertyImageRView(APIView):
    permission_classes = (AllowAny,)
    pk_url_kwarg = 'property_id'

    @swagger_auto_schema(
        operation_summary="Get list of images of the property",
        operation_description="Get the images of the property by the parameter property_id",
        security=[],
        manual_parameters=[openapi.Parameter('property_id',
                                             openapi.IN_PATH,
                                             description="Property ID you want to look up.",
                                             type=openapi.TYPE_STRING)],
        responses={
            '404': 'Property Not Found',
            '200': PropertyImageSerializer
        }
    )
    def get(self, request, property_id):
        property_queryset = Property.objects.filter(property_id=property_id)
        property = get_object_or_404(property_queryset)
        image_queryset = PropertyImage.objects.filter(property_id=property.property_id)
        serializer = PropertyImageSerializer(instance=image_queryset, many=True, context={'request': request})

        return Response(serializer.data, status=200)


class PropertyImageDeleteView(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pk_url_kwarg = ('image_id')

    def delete(self, request, image_id):
        image_queryset = PropertyImage.objects.filter(id=image_id)
        image = get_object_or_404(image_queryset)
        property_id = image.property_id
        user_id = request.user
        property_queryset = Property.objects.filter(owner=user_id)
        property_list = []
        for i in property_queryset:
            property_list.append(i.owner)
        if user_id in property_list:
            image.delete()
            return Response("Delete successful", status=200)
        else:
            return Response("Forbidden", status=403)


class PropertyUDView(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    pk_url_kwarg = ('property_id')

    @swagger_auto_schema(
        operation_summary="Update specific image",
        operation_description="Update the image by the parameter property_id and image_id",
        manual_parameters=[openapi.Parameter('property_id',
                                             openapi.IN_PATH,
                                             description="Property ID you want to modify.",
                                             type=openapi.TYPE_STRING),
                           ],
        request_body=PropertySerializer,
        responses={
            '403': 'Unauthorized',
            '404': 'Not Found',
            '200': PropertySerializer
        }
    )
    def patch(self, request, property_id):
        owner = request.user
        data = request.data
        property_queryset = Property.objects.filter(property_id=property_id)
        property = get_object_or_404(property_queryset)
        if property.owner != owner:
            return Response('Unauthorized', status=403)
        serializer = PropertySerializer(instance=property, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        print(serializer.errors)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_summary="Delete specific property details",
        operation_description="Delete the property details by the parameter property_id",
        manual_parameters=[openapi.Parameter('property_id',
                                             openapi.IN_PATH,
                                             description="Property ID you want to delete.",
                                             type=openapi.TYPE_STRING)],
        responses={
            '403': 'Forbidden',
            '404': 'Property Not Found',
            '200': 'Deletion Successful'
        }
    )
    def delete(self, request, property_id):
        owner = request.user
        property_queryset = Property.objects.filter(property_id=property_id)
        property = get_object_or_404(property_queryset)
        if property.owner != owner:
            return Response('Unauthorized', status=403)
        property.delete()
        return Response('Deletion Successful', status=200)


class PropertySearchView(APIView):
    permission_classes = (AllowAny, )
    pagination_class = None

    @swagger_auto_schema(
        operation_summary="Search properties",
        operation_description="Search properties that matched the given parameters and return a list",
        security=[],
        manual_parameters=[openapi.Parameter('province',
                                             openapi.IN_QUERY,
                                             type=openapi.TYPE_STRING),
                           openapi.Parameter('city',
                                             openapi.IN_QUERY,
                                             type=openapi.TYPE_STRING),
                           openapi.Parameter('price_min',
                                             openapi.IN_QUERY,
                                             type=openapi.TYPE_INTEGER),
                           openapi.Parameter('price_max',
                                             openapi.IN_QUERY,
                                             type=openapi.TYPE_INTEGER),
                           openapi.Parameter('amenities',
                                             openapi.IN_QUERY,
                                             type=openapi.TYPE_STRING),
                           openapi.Parameter('start_date',
                                             openapi.IN_QUERY,
                                             type=openapi.TYPE_STRING),
                           openapi.Parameter('end_date',
                                             openapi.IN_QUERY,
                                             type=openapi.TYPE_STRING),
                           ],
        responses={
            '403': 'Unauthorized',
            '404': 'Not Found',
            '200': PropertySerializer
        }
    )
    def get(self, request, *args, **kwargs):
        province = request.GET.get('province', None)
        city = request.GET.get('city', None)
        price_min = request.GET.get('price_min', None)
        price_max = request.GET.get('price_max', None)
        amenities = request.GET.getlist('amenities', [])
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        sort_by = request.GET.get('sort_by', None)

        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        reserved_properties_queryset = Reservation.objects.filter((Q(status='Approved') | Q(status='Pending')))
        conflict_properties = []
        for obj in reserved_properties_queryset:
            print(obj.start_date)
            print(start_date)
            print(obj.end_date)
            print(end_date)

            if not ((start_date < obj.start_date and end_date < obj.start_date)
                    or (start_date > obj.end_date and end_date > obj.end_date)):
                conflict_properties.append(obj.property_id)

        property_queryset = Property.objects.exclude(property_id__in=conflict_properties)

        if province:
            property_queryset = property_queryset.filter(province__iexact=province)
        if city:
            property_queryset = property_queryset.filter(city__iexact=city)
        if price_min:
            property_queryset = property_queryset.filter(price__gte=price_min)
        if price_max:
            property_queryset = property_queryset.filter(price__lte=price_max)
        if amenities:
            for amenity in amenities:
                property_queryset = property_queryset.filter(amenities__icontains=amenity)

        if sort_by == 'price_low2high':
            property_queryset = property_queryset.order_by('price')
        elif sort_by == 'price_high2low':
            property_queryset = property_queryset.order_by('-price')
        elif sort_by == 'rate_high2low':
            property_queryset = property_queryset.annotate(
                rating_or_zero=ExpressionWrapper(
                    Coalesce('rating', 0),
                    output_field=FloatField()
                )
            ).order_by('-rating_or_zero')
        else:
            property_queryset = property_queryset.annotate(
                rating_or_zero=ExpressionWrapper(
                    Coalesce('rating', 0),
                    output_field=FloatField()
                )
            ).order_by('-rating_or_zero')

        paginator = LimitOffsetPagination()
        paginated_queryset = paginator.paginate_queryset(property_queryset, request)
        serializer = PropertySerializer(paginated_queryset, many=True, context={'request': request})
        return Response({
            'count': paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': serializer.data}, status=200
        )

class PropertyGetMyView(APIView):
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        owner = request.user
        property_queryset = Property.objects.filter(owner=owner)
        serializer = PropertySerializer(instance=property_queryset, many=True, context={'request': request})
        return Response(serializer.data, status=200)





