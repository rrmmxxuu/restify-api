from django.urls import path

from .views import PropertyCreateView, PropertyDetailsView, PropertyUDView, PropertyImageRView, PropertyImageCreateView, PropertySearchView, PropertyGetMyView, PropertyImageDeleteView

app_name = "properties"

urlpatterns = [
    path('create', PropertyCreateView.as_view(), name='create_property'),
    path('modify/<int:property_id>', PropertyUDView.as_view(), name='modify'),
    path('search/', PropertySearchView.as_view(), name='search'),
    path('details/<int:property_id>', PropertyDetailsView.as_view(), name='details'),
    path('image-create/<int:property_id>', PropertyImageCreateView.as_view(), name='image_create'),
    path('image-view/<int:property_id>', PropertyImageRView.as_view(), name='image_view'),
    path('image-delete/<int:image_id>', PropertyImageDeleteView.as_view(), name='image_delete'),
    path('my', PropertyGetMyView.as_view(), name='get_my')
]

