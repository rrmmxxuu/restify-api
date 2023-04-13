from django.db import models

from apps.accounts.models import User

class Notification(models.Model):
    """
    Model for notification
    """

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    message = models.CharField(max_length=150, blank=False, null=False)
    is_read = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
