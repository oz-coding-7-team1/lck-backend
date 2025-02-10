from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.users.views import (  # TermsListView,
    ChangePasswordView,
    MyPageView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    WithdrawAPIView,
)

urlpatterns = [
    path("token/obtain/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("signup/", UserRegisterView.as_view(), name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("withdraw/", WithdrawAPIView.as_view(), name="withdraw"),
    path("mypage/", MyPageView.as_view(), name="mypage"),
    path("password/", ChangePasswordView.as_view(), name="change_password"),
    # path("image/",),
    # path("image/<int:pk>",),
    # path("<int:pk>",),
    # path("terms/", TermsListView.as_view(), name="terms"),
]
