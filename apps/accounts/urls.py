from django.urls import path

from .views import UserDetailView, UserRegisterView, UserChangePasswordView, UserProfileView, UserInfoPublicView, UserProfilePublicView
app_name = "accounts"

urlpatterns = [
    path('register', UserRegisterView.as_view(), name='register'),
    path('user', UserDetailView.as_view(), name='user_info'),
    path('change-password', UserChangePasswordView.as_view(), name='change_password'),
    path('profile', UserProfileView.as_view(), name='profile'),
    path('user-public/<int:user_id>', UserInfoPublicView.as_view(), name='userinfo_public'),
    path('user-profile-public/<int:user_id>', UserProfilePublicView.as_view(), name='userprofile_public')
]

