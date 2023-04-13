from django.urls import path
from .views import ReservationsView, ReservationCreate, ReservationUD

app_name = 'reservations'
urlpatterns = [
    path('details/<int:property_id>', ReservationsView.as_view(), name='reservations_details'),
    path('create/<int:property_id>', ReservationCreate.as_view(), name='reservation_create'),
    path('UD/<int:reservation_id>', ReservationUD.as_view(), name='reservation_UD'),

]