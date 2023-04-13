from django.urls import path

from .views import NotificationCRView, NotificationIsReadView

app_name = "notifications"

urlpatterns = [
    path('', NotificationCRView.as_view(), name='notification'),
    path('is_read/<int:notification_id>', NotificationIsReadView.as_view(), name='set_is_read')
]