from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .choices import AMENITY_CHOICES
from .models import Property, PropertyImage

class PropertySerializer(ModelSerializer):
    """
    Serializer for Property model
    """

    amenities = serializers.MultipleChoiceField(choices=AMENITY_CHOICES, required=False)
    thumbnail = serializers.ImageField()

    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ('owner', 'rating')

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['owner'] = instance.owner.id
    #     return representation

    # def create(self, validated_data):
    #     owner = self.context
    #     validated_data['owner'] = owner
    #     property = Property.objects.create(**validated_data)
    #     return property
    def get_thumbnail(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            else:
                return obj.avatar.url
        return None


class PropertyImageSerializer(ModelSerializer):

    image = serializers.ImageField(required=True)
    class Meta:
        model = PropertyImage
        fields = '__all__'
        read_only_fields = ('property', )


    def get_image(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            else:
                return obj.avatar.url
        return None
        



