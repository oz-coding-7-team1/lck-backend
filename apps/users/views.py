from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Terms, TermsAgreement, User
from .serializers import UserSerializer


# 회원가입 (약관 동의 포함)
class UserRegisterView(APIView):
    permission_classes = (
        AllowAny,
    )

    def post(self, request: Any) -> Response:
        agreed_terms = request.data.get("agreed_terms")
        # isinstance(instance, type): 변수의 타입이 특정 클래스인지 확인
        # 여러개의 약관 id를 담은 리스트 형태로 전달
        if not isinstance(agreed_terms, list):
            raise ParseError("약관 동의 데이터는 리스트 형식이어야 합니다.")

        # 활성화되어 있고 필수인 약관 모두를 가져옴
        required_terms = Terms.objects.filter(is_active=True, is_required=True)
        # 데이터를 집합 자료형으로 변환 / 중복을 제거하고 수학적 집합 연산을 효율적으로 수행할 수 있어서 존재 여부를 빠르게 확인 가능
        required_terms_ids = set(required_terms.values_list("id", flat=True))
        agreed_terms_ids = set(agreed_terms)

        # 필수 약관에 모두 동의했는지 확인
        # A.issubset(B): 집합 A의 모든 요소가 집합 B에 포함되어 있는지 검사
        # 필수 약관 id 집합이 동의한 약관 id 집합에 포함되어야 함
        if not required_terms_ids.issubset(agreed_terms_ids):
            raise ParseError("필수 약관에 모두 동의해야 합니다.")

        password = request.data.get("password")
        serializer = UserSerializer(data=request.data)

        try:
            validate_password(password) # 비밀번호 유효성 검사
        except Exception as e:
            raise ParseError("비밀번호가 유효하지 않습니다. " + str(e))

        if serializer.is_valid(): # 데이터 유효성 검사
            user = serializer.save() # 새로운 유저 생성
            user.set_password(password) # 비밀번호 해시화
            user.save()

            # 사용자가 동의한 약관 기록 생성 (유효한 약관만 처리)
            for term_id in agreed_terms:
                try:
                    term = Terms.objects.get(id=term_id, is_active=True)
                    TermsAgreement.objects.create(user=user, terms=term, is_active=True) # 약관 동의 정보 저장
                except Terms.DoesNotExist:
                    raise ParseError(f"존재하지 않거나 활성화된 약관이 아닙니다: {term_id}")

            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그인
class UserLoginView(APIView):
    permission_classes = (
        AllowAny,
)

    def post(self, request: Any) -> Response:
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None: # 유저가 존재하면 True
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"detail": "잘못된 인증 정보입니다."}, status=status.HTTP_401_UNAUTHORIZED)


# 로그아웃
class UserLogoutView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request: Any) -> Response:
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist() # 로그아웃 시 refresh token을 블랙리스트에 등록
            return Response({"detail": "로그아웃에 성공하였습니다."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 변경
class ChangePasswordView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request: Any) -> Response:
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        # 현재 비밀번호가 맞는지 확인
        # check_password method: 사용자가 입력된 비밀번호와 db에 저장된 해시화 비밀번호를 비교하여 일치하는지 확인
        if not user.check_password(old_password):
            raise PermissionDenied("현재 비밀번호가 일치하지 않습니다.")

        try:
            validate_password(new_password) # 비밀번호 유효성 검사
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


# 약관 리스트 조회 (약관 내용을 확인할 수 있도록)
class TermsListView(APIView):
    permission_classes = (
        AllowAny,
    )

    def get(self, request: Any) -> Response:
        # filter(): 조건에 맞는 쿼리셋을 반환
        # .all() 을 붙여도 동일한 결과를 내지만 중복된 호출이므로 filter(is_active=True) 만 사용
        terms = Terms.objects.filter(is_active=True) # 활성화 된 약관을 조회
        terms_data = [] # TermsList 를 만들기 위한 list
        for term in terms:
            terms_data.append(
                {
                    "id": term.id,
                    "name": term.name,
                    "detail": term.detail,
                    "is_required": term.is_required,
                }
            )
        return Response(terms_data, status=status.HTTP_200_OK)


# 회원정보 조회, 수정 (MyPage)
class MyPageView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    # 조회
    def get(self, request: Any) -> Response:
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 수정
    def put(self, request: Any) -> Response:
        user = get_object_or_404(User, id=request.data["id"])
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            user = serializer.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
