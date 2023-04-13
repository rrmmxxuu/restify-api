from django.db import models

from multiselectfield import MultiSelectField

from apps.accounts.models import User
from apps.properties.choices import AMENITY_CHOICES, PROVINCE_CHOICES,  PROPERTY_TYPE_CHOICES

# Create your models here.

class Property(models.Model):
    """
    Model that stores the property information
    """
    property_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=150, blank=False, null=False)
    address = models.CharField(max_length=150, blank=False, null=False)
    city = models.CharField(max_length=150, blank=False, null=False)
    province = models.CharField(max_length=150, choices=PROVINCE_CHOICES, blank=False, null=False)
    postal_code = models.CharField(max_length=10, blank=False, null=False)
    price = models.IntegerField(blank=False, null=False)
    property_type = models.CharField(max_length=150, choices=PROPERTY_TYPE_CHOICES, blank=False, null=False)
    num_bedrooms = models.IntegerField(blank=False, null=False)
    sqft = models.IntegerField(blank=False, null=False)
    amenities = MultiSelectField(max_length=200, choices=AMENITY_CHOICES, blank=True, null=True)
    thumbnail = models.ImageField(blank=True, default='default_property_image', upload_to='property_thumbnails')
    rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True, default=None)

    time_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title + "of" + str(self.owner.id)


class PropertyImage(models.Model):
    """
    Model that stores images for the property
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

    image = models.ImageField(blank=False, default='default_property_image', upload_to='property_images')
    image_name = models.CharField(max_length=150, blank=False, null=False)

    def __str__(self):
        return self.image_name + "of" + str(self.property.id)

