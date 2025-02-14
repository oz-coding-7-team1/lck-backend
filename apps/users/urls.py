from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenVerifyView,
)

from apps.users.views import (
    ChangePasswordView,
    LoginView,
    LogoutView,
    MyPageView,
    RefreshTokenView,
    SignupView,
    TermsAgreementListView,
    TermsAgreementUpdateView,
    TermsListView,
    WithdrawView,
)

urlpatterns = [
    path("token/obtain/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("withdraw/", WithdrawView.as_view(), name="withdraw"),
    path("mypage/", MyPageView.as_view(), name="mypage"),
    path("password/", ChangePasswordView.as_view(), name="change_password"),
    path("terms/", TermsListView.as_view(), name="terms_list"),
    path("terms/agree/", TermsAgreementListView.as_view(), name="terms_agreements_list"),
    path("terms/agree/<int:pk>/", TermsAgreementUpdateView.as_view(), name="terms_agreement_update"),
]
