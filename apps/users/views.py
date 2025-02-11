from typing import Any

from django.conf import settings
from django.contrib.auth import authenticate, logout
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Terms, TermsAgreement, User
from .serializers import UserRegisterSerializer, UserSerializer, UserLoginSerializer, MypageSerializer, \
    ChangePasswordSerializer


# 회원가입 (약관 동의 포함)
class UserRegisterView(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    @extend_schema(
        request=UserRegisterSerializer,
        responses={
            201: UserRegisterSerializer,
            400: dict,
        },
        summary="회원가입",
        description="이메일, 닉네임, 비밀번호 등 회원 정보를 입력받아 새 사용자를 생성합니다.",
    )
    def post(self, request: Any) -> Response:
        # agreed_terms = request.data.get("agreed_terms")
        # # isinstance(instance, type): 변수의 타입이 특정 클래스인지 확인
        # # 여러개의 약관 id를 담은 리스트 형태로 전달
        # if not isinstance(agreed_terms, list):
        #     raise ParseError("약관 동의 데이터는 리스트 형식이어야 합니다.")
        #
        # # 활성화되어 있고 필수인 약관 모두를 가져옴
        # required_terms = Terms.objects.filter(is_active=True, is_required=True)
        # # 데이터를 집합 자료형으로 변환 / 중복을 제거하고 수학적 집합 연산을 효율적으로 수행할 수 있어서 존재 여부를 빠르게 확인 가능
        # required_terms_ids = set(required_terms.values_list("id", flat=True))
        # agreed_terms_ids = set(agreed_terms)
        #
        # # 필수 약관에 모두 동의했는지 확인
        # # A.issubset(B): 집합 A의 모든 요소가 집합 B에 포함되어 있는지 검사
        # # 필수 약관 id 집합이 동의한 약관 id 집합에 포함되어야 함
        # if not required_terms_ids.issubset(agreed_terms_ids):
        #     raise ParseError("필수 약관에 모두 동의해야 합니다.")

        password = request.data.get("password")
        serializer = UserRegisterSerializer(data=request.data)

        try:
            validate_password(password)  # 비밀번호 유효성 검사
        except Exception as e:
            raise ParseError("비밀번호가 유효하지 않습니다. " + str(e))

        if serializer.is_valid():  # 데이터 유효성 검사
            user = serializer.save()  # 새로운 유저 생성
            user.set_password(password)  # 비밀번호 해시화
            user.save()

            #     # 사용자가 동의한 약관 기록 생성 (유효한 약관만 처리)
            #     for term_id in agreed_terms:
            #         try:
            #             term = Terms.objects.get(id=term_id, is_active=True)
            #             TermsAgreement.objects.create(user=user, terms=term, is_active=True)  # 약관 동의 정보 저장
            #         except Terms.DoesNotExist:
            #             raise ParseError(f"존재하지 않거나 활성화된 약관이 아닙니다: {term_id}")
            #
            serializer = UserRegisterSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그인
class UserLoginView(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: dict,
            401: dict,
        },
        summary="로그인",
        description="이메일과 비밀번호로 사용자를 인증하여 JWT 토큰을 발급합니다.",
    )

    def post(self, request: Any) -> Response:
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:  # 유저가 존재하면 True
            refresh = RefreshToken.for_user(user)  # JWT token 생성
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # access token 은 JSON 응답으로 반환
            response = Response({"access_token": access_token}, status=status.HTTP_200_OK)
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
            return Response({"detail": "잘못된 인증 정보입니다."}, status=status.HTTP_401_UNAUTHORIZED)

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
class UserLogoutView(APIView):
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
class WithdrawAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

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
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

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
        user = get_object_or_404(User, id=request.data["id"])
        serializer = MypageSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            user = serializer.save()
            serializer = MypageSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 변경
class ChangePasswordView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

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


# # 약관 리스트 조회 (약관 내용을 확인할 수 있도록)
# class TermsListView(APIView):
#     permission_classes = (AllowAny,)
#
#     def get(self, request: Any) -> Response:
#         # filter(): 조건에 맞는 쿼리셋을 반환
#         # .all() 을 붙여도 동일한 결과를 내지만 중복된 호출이므로 filter(is_active=True) 만 사용
#         terms = Terms.objects.filter(is_active=True)  # 활성화 된 약관을 조회
#         terms_data = []  # TermsList 를 만들기 위한 list
#         for term in terms:
#             terms_data.append(
#                 {
#                     "id": term.id,
#                     "name": term.name,
#                     "detail": term.detail,
#                     "is_required": term.is_required,
#                 }
#             )
#         return Response(terms_data, status=status.HTTP_200_OK)
