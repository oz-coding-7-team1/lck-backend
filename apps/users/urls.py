from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.users.views import (
    ChangePasswordView,
    MyPageView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
)

urlpatterns = [
    path("obtain/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("signup/", UserRegisterView.as_view(), name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    # path("Withdrawal/",),
    path("user/mypage/", MyPageView.as_view(), name="mypage"),
    path("user/password/", ChangePasswordView.as_view(), name="change-password"),
    # path("user/image/",),
    # path("user/image/<int:pk>",),
    # path("user/<int:pk>",),
]
