from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Terms, TermsAgreement, User

# 테스트에 사용할 기본 데이터 (일반 사용자, 슈퍼유저)
data = {"email": "test@gmail.com", "nickname": "testuser", "password": "password"}
super_data = {"email": "super@gmail.com", "nickname": "superuser", "password": "password"}

# 인증이 필요한 테스트에서 공통적으로 사용할 클래스
class APITestCaseSetUp(APITestCase):
    def setUp(self) -> None:
        # 테스트 환경에서 해당 속성이 없으면 기본값 (False) 으로 설정
        if not hasattr(settings, "REFRESH_TOKEN_COOKIE_SECURE"):
            settings.REFRESH_TOKEN_COOKIE_SECURE = False
        # 테스트용 일반 사용자 생성
        self.user = User.objects.create_user(email=data["email"], nickname=data["nickname"], password=data["password"]) # type: ignore
        # JWT access token 생성 후 클라이언트 헤더에 등록
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")


# 사용자와 슈퍼유저 생성 권한 테스트
class CreateUserAuthorizedTestCase(APITestCaseSetUp):
    # 일반 사용자 생성 후 필드 값 검증
    def test_create_user(self) -> None:
        self.assertEqual(self.user.email, data["email"])
        self.assertTrue(self.user.check_password(data["password"]))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    # 슈퍼유저 생성 후 필드 값 검증
    def test_create_superuser(self) -> None:
        super_user = get_user_model().objects.create_superuser(
            email=super_data["email"], nickname="superuser", password=super_data["password"]
        )
        self.assertEqual(super_user.email, super_data["email"])
        self.assertTrue(super_user.check_password(super_data["password"]))
        self.assertTrue(super_user.is_active)
        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_superuser)


# 로그인 및 로그아웃 API 테스트
class JWTAuthTestCase(APITestCaseSetUp):
    # 로그인 테스트: 올바른 이메일과 비밀번호를 전송하면 access token 이 JSON 응답에 포함되고, refresh token 은 httpOnly 쿠키에 설정
    def test_login_success(self) -> None:
        url = reverse("login")
        response = self.client.post(url, data={"email": data["email"], "password": data["password"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 로그인 API는 JSON에 "access_token" 키로 토큰을 반환함
        self.assertIn("access_token", response.data)
        # refresh token은 쿠키에 설정되었는지 확인
        self.assertIn("refresh_token", response.cookies)

    def test_logout_success(self) -> None:
        # 로그아웃 테스트: 클라이언트에 refresh token 쿠키가 있으면 로그아웃 후 쿠키가 삭제
        url = reverse("logout")
        # 테스트용으로 refresh token 쿠키 설정
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["refresh_token"] = str(refresh)
        response = self.client.post(url)
        refresh_cookie = response.cookies.get("refresh_token")
        # 쿠키가 존재하면 값이 빈 문자열이어야 함
        if refresh_cookie is not None:
            self.assertEqual(refresh_cookie.value, "")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# 회원가입 API 테스트 (약관 동의 추가)
class UserRegistrationTestCase(APITestCase):
    def setUp(self) -> None:
        self.registration_url = reverse("signup")
        # DB 에 존재하는 모든 Terms 를 삭제하여, 테스트에 영향을 주지 않도록 함
        Terms.objects.all().delete()
        # 테스트용으로 필수 약관과 선택 약관을 생성 (필수 약관은 반드시 동의해야 함)
        self.required_term = Terms.objects.create(
            name="Required Terms", detail="required details", is_required=True, is_active=True
        )
        self.optional_term = Terms.objects.create(
            name="Optional Terms", detail="optional details", is_required=False, is_active=True
        )
        self.user_data = {
            "email": "newuser@example.com",
            "password": "StrongPassw0rd!",
            "nickname": "newuser",
            # 필수 약관과 선택 약관 모두 동의한 것으로 전송 (각 항목은 dict 형태로 전달)
            "terms_agreements": [
                {"terms": self.required_term.id, "is_active": True},
                {"terms": self.optional_term.id, "is_active": True},
            ],
        }

    def test_registration_success(self) -> None:
        # 회원가입 성공 테스트: 올바른 데이터를 전송하면 회원가입 완료
        response = self.client.post(self.registration_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], self.user_data["email"])

    def test_registration_fail_missing_required_terms(self) -> None:
        # 회원가입 실패 테스트: 필수 약관 동의 누락 시 회원가입 실패
        user_data = self.user_data.copy()
        # 필수 약관 미동의 (옵션 약관만 전송)
        user_data["terms_agreements"] = [
            {"terms": self.optional_term.id, "is_active": True},
        ]
        response = self.client.post(self.registration_url, user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_rail_invalid_terms_agreements_format(self) -> None:
        # 회원가입 실패 테스트: 약관 동의 데이터가 리스트 형식이 아닌 경우 오류 발생
        user_data = self.user_data.copy()
        user_data["terms_agreements"] = "not a list"  # 잘못된 형식
        response = self.client.post(self.registration_url, user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_fail_invalid_password(self) -> None:
        # 회원가입 실패 테스트: 유효하지 않은(예: 너무 약한) 비밀번호를 전송하면 회원가입 실패
        user_data = self.user_data.copy()
        user_data["password"] = "123"  # 일반적으로 유효하지 않은 비밀번호
        response = self.client.post(self.registration_url, user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# access token 재발급 API 테스트
class RefreshTokenTestCase(APITestCaseSetUp):
    def setUp(self) -> None:
        super().setUp()
        self.refresh_url = reverse("token_refresh")
        # 클라이언트 쿠키에 refresh token을 수동으로 추가
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.client.cookies["refresh_token"] = self.refresh_token

    def test_refresh_token_success(self) -> None:
        # refresh token 재발급 성공 테스트: 쿠키에 저장된 refresh token 을 사용해 새로운 access token 이 발급 되어야 함
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # JSON 응답에 "access_token" 키로 새 access token 이 반환됨
        self.assertIn("access_token", response.data)
        # 응답 쿠키에 새 refresh token 이 설정되었는지 확인 (값이 빈 문자열이 아니어야 함)
        new_refresh_token = response.cookies.get("refresh_token")
        self.assertIsNotNone(new_refresh_token)
        self.assertNotEqual(new_refresh_token, "")

    def test_refresh_token_fail_no_cookie(self) -> None:
        # refresh token 재발급 실패 테스트: refresh token 쿠키가 없으면 에러 응답 반환
        self.client.cookies.clear()
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# 회원 탈퇴 API 테스트
class WithdrawTestCase(APITestCaseSetUp):
    def setUp(self) -> None:
        super().setUp()
        self.withdraw_url = reverse("withdraw")
        # 회원 탈퇴 시에도 refresh token 을 블랙리스트에 추가해야 하므로 쿠키에 추가
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.client.cookies["refresh_token"] = self.refresh_token

    def test_withdraw_success(self) -> None:
        # 회원 탈퇴 성공 테스트: 회원 탈퇴 API 호출 시 사용자의 계정이 삭제(soft delete)되고, refresh token 쿠키 삭제
        response = self.client.post(self.withdraw_url)
        refresh_cookie = response.cookies.get("refresh_token")
        # 쿠키가 존재하면 값이 빈 문자열이어야 함
        if refresh_cookie is not None:
            self.assertEqual(refresh_cookie.value, "")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "회원 탈퇴가 완료되었습니다.")


# 마이페이지 - 회원정보 조회 및 수정 API 테스트
class MyPageTestCase(APITestCaseSetUp):
    def setUp(self) -> None:
        super().setUp()
        self.mypage_url = reverse("mypage")

    def test_get_user_unauthorized(self) -> None:
        # 인증 없이 회원정보 조회 테스트: 로그인이 되어 있지 않으면 401 Unauthorized 응답 반환
        self.client.logout()
        response = self.client.get(self.mypage_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_authorized(self) -> None:
        # 인증 후 회원정보 조회 테스트: 올바른 인증 정보가 있으면 회원정보가 정상적으로 조회됨
        # APITestCaseSetUp 에서 이미 인증 헤더를 설정했으므로 별도 로그인 불필요
        response = self.client.get(self.mypage_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], data["email"])

    def test_update_user_success(self) -> None:
        # 회원정보 수정 테스트: 요청 데이터에 사용자 id 가 포함되어 있어야하고, PUT 요청으로 일부 필드를 수정할 수 있어야 함
        update_data = {"id": self.user.id, "nickname": "Updated Nickname"}
        response = self.client.put(self.mypage_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(response.data.get("nickname"), "Updated Nickname")


# 비밀번호 변경 API 테스트
class ChangePasswordTestCase(APITestCaseSetUp):
    def setUp(self) -> None:
        super().setUp()
        self.change_password_url = reverse("change_password")

    def test_change_password_success(self) -> None:
        # 비밀번호 변경 성공 테스트: 기존 비밀번호와 새 비밀번호를 전송하면 비밀번호가 성공적으로 변경
        change_data = {"old_password": data["password"], "new_password": "NewStrongPassw0rd!"}
        response = self.client.post(self.change_password_url, change_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "비밀번호가 성공적으로 변경되었습니다.")

    def test_change_password_fail_incorrect_old_password(self) -> None:
        # 비밀번호 변경 실패 테스트: 현재 비밀번호가 틀린 경우, 변경 불가
        change_data = {"old_password": "wrong_password", "new_password": "NewStrongPassw0rd!"}
        response = self.client.post(self.change_password_url, change_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# 약관 리스트 조회 API 테스트
class TermsListTestCase(APITestCase):
    def setUp(self) -> None:
        self.terms_list_url = reverse("terms_list")
        Terms.objects.all().delete()
        # 활성화된 약관 2개와 비활성 약관 1개 생성
        Terms.objects.create(name="약관1", detail="내용1", is_required=True, is_active=True)
        Terms.objects.create(name="약관2", detail="내용2", is_required=False, is_active=True)
        Terms.objects.create(name="약관3", detail="내용3", is_required=True, is_active=False)

    def test_terms_list(self) -> None:
        # 약관 리스트 조회 테스트: GET 요청 시 활성화된 약관만 리스트로 반환
        response = self.client.get(self.terms_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 활성화된 약관은 2개여야 함
        self.assertEqual(len(response.data), 2)
        # 각 약관에 필요한 필드가 포함되어 있는지 확인
        for term in response.data:
            self.assertIn("id", term)
            self.assertIn("name", term)
            self.assertIn("detail", term)
            self.assertIn("is_active", term)
            self.assertIn("is_required", term)
