from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    ProfileAPIView,
    TokenRefreshAPIView,
    LogoutAPIView,
    ChangePasswordAPIView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
    )

urlpatterns = [
    path("register/",RegisterAPIView.as_view(),name="register"),
    path("login/",LoginAPIView.as_view(),name="login"),
    path("profile/",ProfileAPIView.as_view(),name="profile"),
    path("token/refresh/",TokenRefreshAPIView.as_view(),name="token_refresh"),
    path("logout/",LogoutAPIView.as_view(),name="logout"),
    path("change-password/",ChangePasswordAPIView.as_view(),name="change_password"),
    path("password-reset/",PasswordResetRequestAPIView.as_view(),name="password-reset"),
    path("password-reset/confirm/",PasswordResetConfirmAPIView.as_view(),name="password-reset-confirm"),
]

