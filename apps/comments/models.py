from django.db import models
from ..accounts.models import User
from ..reservations.models import Reservation
from ..properties.models import Property
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    content = models.TextField()
    # parent_comment used for identify whether the comment is a followup and used to create an ordered comments line
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    RATING_CHOICES = [
        (1, '1 star'),
        (2, '2 stars'),
        (3, '3 stars'),
        (4, '4 stars'),
        (5, '5 stars'),
    ]
    rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=Comments)
def update_property_rating(sender, instance, **kwargs):
    property = instance.property
    related_comments = Comments.objects.filter(property=property)

    total_rating = sum(comment.rating for comment in related_comments if comment.rating)
    total_rated_comments = sum(1 for comment in related_comments if comment.rating)
    average_rating = total_rating / total_rated_comments if total_rated_comments > 0 else 0

    property.rating = average_rating
    property.save()



