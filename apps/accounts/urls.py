from django.urls import path

from .views import UserDetailView, UserRegisterView, UserChangePasswordView, UserProfileView
app_name = "accounts"

urlpatterns = [
    path('register', UserRegisterView.as_view(), name='register'),
    path('user', UserDetailView.as_view(), name='user_info'),
    path('change-password', UserChangePasswordView.as_view(), name='change_password'),
    path('profile', UserProfileView.as_view(), name='profile')
]

