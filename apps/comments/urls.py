from django.urls import path
from .views import CommentsDetails, CommentCreate, CommentUD, PropertyComments

app_name = 'comments'
urlpatterns = [
    path('details/<int:reservation_id>', CommentsDetails.as_view(), name='comments_details'),
    path('create/<int:reservation_id>', CommentCreate.as_view(), name='comment_create'),
    path('UD/<int:comment_id>', CommentUD.as_view(), name='comment_UD'),
    path('property/<int:property_id>', PropertyComments.as_view(), name='property_comments'),

]