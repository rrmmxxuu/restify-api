from django.db import models
from ..accounts.models import User
from ..properties.models import Property
# Create your models here.


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Denied', 'Denied'),
        ('Expired', 'Expired'),
        ('Approved', 'Approved'),
        ('Canceled', 'Canceled'),
        ('Terminated', 'Terminated'),
        ('Completed', 'Completed')
    ]

    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


