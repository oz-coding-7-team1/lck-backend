from typing import Any, List

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.permissions import (
    AllowAny,
    BasePermission,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenVerifyView

from .models import Terms, TermsAgreement, User
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    MypageSerializer,
    SignupSerializer,
    TermsAgreementSerializer,
    TermsSerializer,
    UserSerializer,
)


# 회원가입 (약관 동의 포함)
class SignupView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(
        request=SignupSerializer,
        responses={
            201: UserSerializer,
            400: dict,
        },
        summary="회원가입",
        description="이메일, 닉네임, 비밀번호 등 회원 정보를 입력받아 새 사용자를 생성합니다.",
    )
    def post(self, request: Any) -> Response:
        password = request.data.get("password")
        serializer = SignupSerializer(data=request.data)

        try:
            validate_password(password)  # 비밀번호 유효성 검사
        except Exception as e:
            raise ParseError("비밀번호가 유효하지 않습니다. " + str(e))

        if serializer.is_valid():  # 데이터 유효성 검사
            user = serializer.save()  # 새로운 유저 생성
            user.save()

            user_serializer = UserSerializer(user)
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그인
class LoginView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: dict,
            401: dict,
        },
        summary="로그인",
        description="이메일과 비밀번호로 사용자를 인증하여 JWT 토큰을 발급합니다.",
    )
    def post(self, request: Any) -> Response:
        email = request.data.get("email")
        if not email:
            return Response({"detail": "이메일을 입력하세요"}, status=status.HTTP_400_BAD_REQUEST)
        password = request.data.get("password")
        if not password:
            return Response({"detail": "비밀번호를 입력하세요"}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(email=email, password=password)

        if not User.objects.filter(email=email).exists():
            return Response({"detail": "존재하지 않는 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if user is not None:  # 유저인증에 성공하면 True
            refresh = RefreshToken.for_user(user)  # JWT token 생성
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            user_data = User.objects.get(email=email)
            serializer = UserSerializer(user_data)

            # access token 은 JSON 응답으로 반환
            response = Response({"access_token": access_token, "user": serializer.data}, status=status.HTTP_200_OK)
            # refresh token 은 httpOnly, secure cookie 에 저장
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,  # 자바스크립트에서 접근 불가능하게 설정
                secure=settings.REFRESH_TOKEN_COOKIE_SECURE,  # True: HTTPS 환경에서만 쿠키가 전송되도록 함
                samesite="Strict",  # 같은 사이트에서만 쿠키 전송
            )
            return response
        else:
            return Response({"detail": "잘못된 비밀번호입니다."}, status=status.HTTP_401_UNAUTHORIZED)

    """
    - set_cookie 메서드 (응답 헤더에 쿠키를 설정하게 해주는 메서드)
        httponly=True: 자바스크립트 코드에서 해당 쿠키에 접근할 수 없게 만드는 옵션 (XSS 공격 시 악의적인 스크립트가 쿠키에 저장된 민감한 정보를 읽어가는 것을 방지)
        secure=True: 해당 쿠키는 HTTPS (보안 연결) 를 통해서만 브라우저와 서버 간의 전송이 가능해짐 -> 개발 환경에서는 False 로 설정 가능
        samesite="Strict": 쿠키가 오직 동일 사이트 (현재 도메인에서 발생하는 요청) 에만 전송되도록 제한 (CSRF 공격을 방어할 수 있음) -> 추후 소셜로그인 추가 시 None 으로 변경하고 다른 방어를 강화할 필요 요망
       
    - XSS (크로스 사이트 스크립팅): 공격자가 웹 애플리케이션에 악성 스크립트를 삽입하여, 다른 사용자의 브라우저에서 실행되도록 만드는 공격
            예) 세션 쿠키, 인증 정보, 민감 데이터 탈취
    - CSRF (크로스 사이트 요청 위조): 사용자가 이미 인증된 상태에서, 악의적인 사이트나 스크립트가 사용자의 의지와 상관없이 해당 사용자의 권한으로 요청을 보내도록 유도하는 공격
            예) 사용자의 인증 정보를 바탕으로 금전 이체, 개인정보 변경 등 원치 않는 작업 실행
    """


# verify에 권한 추가
class CustomTokenVerifyView(TokenVerifyView):
    permission_classes = (IsAuthenticated,)  # type: ignore
    authentication_classes = (JWTAuthentication,)  # type: ignore


# access token 재발급
class RefreshTokenView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        responses={
            200: TokenRefreshSerializer,
            401: dict,
            403: dict,
        },
        summary="Access Token 재발급",
        description="쿠키에 저장된 refresh token 을 이용하여 새로운 access token 을 발급합니다.",
    )
    def post(self, request: Any) -> Response:
        # 쿠키에서 refresh token 가져오기
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "Refresh token 이 제공되지 않았습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # 기존 리프레쉬 토큰 검증
            old_refresh = RefreshToken(refresh_token)
            user_id = old_refresh.payload.get("user_id")
            if not user_id:
                raise Exception("유저 정보가 존재하지 않습니다.")
            user = User.objects.get(id=user_id)

            # 기존 refresh token 블랙리스트 처리
            old_refresh.blacklist()

            # 새 refresh token 생성
            new_refresh = RefreshToken.for_user(user)
            new_access_token = str(new_refresh.access_token)

            # body 에 access token 만 포함한 응답 생성
            response = Response({"access_token": new_access_token}, status=status.HTTP_200_OK)

            # 새 refresh token 을 쿠키에 설정
            response.set_cookie(
                key="refresh_token",
                value=str(new_refresh),
                httponly=True,
                secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
                samesite="Strict",
            )
            return response
        except:
            return Response({"detail": "잘못된 refresh token 입니다."}, status=status.HTTP_403_FORBIDDEN)


# 로그아웃
class LogoutView(APIView):
    @extend_schema(
        responses={
            204: dict,
            400: dict,
        },
        summary="로그아웃",
        description="refresh token 을 블랙리스트에 등록하고 쿠키를 삭제합니다.",
    )
    def post(self, request: Any) -> Response:
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()  # 로그아웃 시 refresh token을 블랙리스트에 등록
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        response = Response({"detail": "로그아웃 되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("refresh_token")
        return response


# 회원 탈퇴
class WithdrawView(APIView):
    @extend_schema(
        responses={
            200: dict,
            400: dict,
        },
        summary="회원 탈퇴",
        description="회원 탈퇴 시 refresh token 을 블랙리스트에 등록하고 soft delete 처리합니다.",
    )
    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        # 쿠키에서 refresh token 추출
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()  # refresh token 을 블랙리스트에 등록
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # soft delete 처리 (탈퇴 상태로 저장)
        user = request.user
        user.delete()

        # refresh token 삭제 후 응답 반환
        response = Response({"detail": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")
        return response


# 회원정보 조회, 수정 (MyPage)
class MyPageView(APIView):

    @extend_schema(
        responses={200: MypageSerializer},
        summary="회원정보 조회",
        description="현재 로그인한 사용자의 정보를 조회합니다.",
    )
    # 조회
    def get(self, request: Any) -> Response:
        user = request.user
        serializer = MypageSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=MypageSerializer,
        responses={
            200: MypageSerializer,
            400: dict,
        },
        summary="회원정보 수정",
        description="회원정보를 부분 업데이트합니다.",
    )
    # 수정
    def put(self, request: Any) -> Response:
        user = get_object_or_404(User, id=request.user.id)
        serializer = MypageSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            user = serializer.save()
            serializer = MypageSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 변경
class ChangePasswordView(APIView):

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: dict,
            400: dict,
            403: dict,
        },
        summary="비밀번호 변경",
        description="현재 비밀번호와 새 비밀번호를 받아 비밀번호를 변경합니다.",
    )
    def post(self, request: Any) -> Response:
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        # 현재 비밀번호가 맞는지 확인
        # check_password method: 사용자가 입력된 비밀번호와 db에 저장된 해시화 비밀번호를 비교하여 일치하는지 확인
        if not user.check_password(old_password):
            raise PermissionDenied("현재 비밀번호가 일치하지 않습니다.")

        try:
            validate_password(new_password)  # 비밀번호 유효성 검사
        except Exception as e:
            raise ParseError("새 비밀번호가 유효하지 않습니다. " + str(e))

        user.set_password(new_password)
        user.save()
        return Response({"detail": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)

    """
    - 역직렬화는 클라이언트에게 객체의 상세 정보를 전달할 때 사용되므로 비밀번호 변경 후 사용자 정보를 재전달할 필요 없이 성공 메세지만 전달
    - set_password 와 save 메서드 만으로 변경된 비밀번호가 DB에 자동 저장됨
    - 비밀번호 저장 방식
        1. user.set_password(new_password)를 호출하면, 입력한 새로운 비밀번호를 내부적으로 안전하게 해싱한 후 사용자 객체에 저장
        2. user.save() 호출: 변경된 사용자 객체 상태가 데이터베이스에 반영
    """


# 약관 정보 생성 및 약관 전체 내역 조회
class TermsListView(APIView):

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]  # POST 요청은 관리자만 허용
        return [AllowAny()]  # GET 요청은 아무나 허용

    @extend_schema(
        responses={200: TermsSerializer(many=True)},
        summary="약관 목록 조회",
        description="활성화된 약관 목록을 조회합니다.",
    )
    def get(self, request: Any) -> Response:
        terms = Terms.objects.filter(is_active=True)
        serializer = TermsSerializer(terms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=TermsSerializer,
        responses={
            201: TermsSerializer,
            400: dict,
        },
        summary="약관 생성",
        description="새로운 약관 내용을 생성합니다. 필드: name, detail, is_active, is_required",
    )
    def post(self, request: Any) -> Response:
        serializer = TermsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # 새 약관 생성
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 사용자 약관 동의 내역 조회
class TermsAgreementListView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        responses={200: TermsAgreementSerializer(many=True)},
        summary="사용자 약관 동의 내역 조회",
        description="현재 로그인한 사용자의 약관 동의 내역을 조회합니다.",
    )
    def get(self, request: Any) -> Response:
        agreement = TermsAgreement.objects.filter(user=request.user)
        serializer = TermsAgreementSerializer(agreement, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 선택적 약관 동의 수정
class TermsAgreementUpdateView(APIView):
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )

    @extend_schema(
        request=TermsAgreementSerializer,
        responses={
            200: TermsAgreementSerializer,
            400: dict,
            404: dict,
        },
        summary="선택적 약관 동의 수정",
        description="로그인 사용자가 선택적으로 동의한 약관의 일부 내용을 수정합니다. 단, 필수 약관은 수정할 수 없습니다.",
    )
    def patch(self, request: Any, pk: int, *args: Any, **kwargs: Any) -> Response:
        try:
            agreement = TermsAgreement.objects.get(pk=pk, user=request.user)
        except TermsAgreement.DoesNotExist:
            return Response({"detail": "해당 약관 동의 정보가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 필수 약관은 수정 불가능
        if agreement.terms.is_required:
            return Response({"detail": "필수 약관은 수정할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TermsAgreementSerializer(agreement, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
