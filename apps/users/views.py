from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Terms, TermsAgreement
from .serializers import UserSerializer


# 회원가입 (약관 동의 포함)
class UserRegisterView(APIView):
    permission_classes = [AllowAny,]

    def post(self, request):
        agreed_terms = request.data.get("agreed_terms")
        # isinstance(instance, type): 변수의 타입이 특정 클래스인지 확인
        # 여러개의 약관 id를 담은 리스트 형태로 전달
        if not isinstance(agreed_terms, list):
            raise ParseError("약관 동의 데이터는 리스트 형식이어야 합니다.")

        # 활성화되어 있고 필수인 약관 모두를 가져옴
        required_terms = Terms.objects.filter(is_active=True, is_required=True)
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
            validate_password(password)
        except Exception as e:
            raise ParseError("비밀번호가 유효하지 않습니다. " + str(e))

        if serializer.is_valid():
            user = serializer.save()
            user.set_password(password)
            user.save()

            # 사용자가 동의한 약관 기록 생성 (유효한 약관만 처리)
            for term_id in agreed_terms:
                try:
                    term = Terms.objects.get(id=term_id, is_active=True)
                    TermsAgreement.objects.create(user=user, terms=term, is_active=True)
                except Terms.DoesNotExist:
                    raise ParseError(f"존재하지 않거나 활성화된 약관이 아닙니다: {term_id}")

            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그인
class UserLoginView(APIView):
    permission_classes = [AllowAny,]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "잘못된 인증 정보입니다."}, status=status.HTTP_401_UNAUTHORIZED)


# 로그아웃
class UserLogoutView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "로그아웃에 성공하였습니다."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 변경
class ChangePasswordView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        # 현재 비밀번호 확인
        if not user.check_password(old_password):
            raise PermissionDenied("현재 비밀번호가 일치하지 않습니다.")

        try:
            validate_password(new_password)
        except Exception as e:
            raise ParseError("새 비밀번호가 유효하지 않습니다. " + str(e))

        user.set_password(new_password)
        user.save()
        return Response({"detail": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)


# 약관 리스트 조회 (약관 내용을 확인할 수 있도록)
class TermsListView(APIView):
    permission_classes = [AllowAny,]

    def get(self, request):
        terms = Terms.objects.filter(is_active=True)
        terms_data = []
        for term in terms:
            terms_data.append({
                "id": term.id,
                "name": term.name,
                "detail": term.detail,
                "is_required": term.is_required,
            })
        return Response(terms_data, status=status.HTTP_200_OK)