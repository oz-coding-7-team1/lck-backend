from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Terms, TermsAgreement, User

# 테스트에 사용할 기본 데이터 (일반 사용자, 슈퍼유저)
data = {"email": "test@gmail.com", "password": "password"}
super_data = {"email": "super@gmail.com", "password": "password"}


# 인증이 필요한 테스트에서 공통적으로 사용할 클래스
class APITestCaseSetUp(APITestCase):
    def setUp(self) -> None:
        # 테스트용 일반 사용자 생성
        self.user = User.objects.create_user(email=data["email"], password=data["password"])
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
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.user.is_superuser)

    # 슈퍼유저 생성 후 필드 값 검증
    def test_create_superuser(self) -> None:
        super_user = get_user_model().objects.create_superuser(super_data["email"], super_data["password"])
        self.assertEqual(super_user.email, super_data["email"])
        self.assertTrue(super_user.check_password(super_data["password"]))
        self.assertTrue(super_user.is_active)
        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_admin)
        self.assertTrue(super_user.is_superuser)


# 로그인 및 로그아웃 API 테스트
class JWTAuthTestCase(APITestCaseSetUp):
    def test_login_success(self) -> None:
        """
        로그인 API 테스트:
        - 올바른 이메일과 비밀번호를 전송하면 access token이 JSON 응답에 포함되고,
          refresh token은 httpOnly 쿠키에 설정되어야 합니다.
        """
        url = reverse("login")
        response = self.client.post(url, data={"email": data["email"], "password": data["password"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 로그인 API는 JSON에 "access_token" 키로 토큰을 반환함
        self.assertIn("access_token", response.data)
        # refresh token은 쿠키에 설정되었는지 확인
        self.assertIn("refresh_token", response.cookies)

    def test_logout_success(self) -> None:
        """
        로그아웃 API 테스트:
        - 클라이언트에 refresh token 쿠키가 있으면 로그아웃 후 쿠키가 삭제되어야 합니다.
        """
        url = reverse("logout")
        # 테스트용으로 refresh token 쿠키 설정
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["refresh_token"] = str(refresh)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # 로그아웃 응답 시 쿠키가 삭제되었는지 확인 (쿠키의 삭제 여부는 응답 쿠키에서 확인)
        self.assertNotIn("refresh_token", response.cookies)


# 회원가입 API 테스트
class UserRegistrationTestCase(APITestCase):
    def setUp(self) -> None:
        # # 회원가입 시 필요한 약관 데이터 생성 (필수 약관과 선택 약관)
        # self.required_term = Terms.objects.create(
        #     name="필수 약관", detail="필수 약관 내용", is_required=True, is_active=True
        # )
        # self.optional_term = Terms.objects.create(
        #     name="선택 약관", detail="선택 약관 내용", is_required=False, is_active=True
        # )
        self.registration_url = reverse("signup")
        self.user_data = {
            "email": "newuser@example.com",
            "password": "StrongPassw0rd!",
            # 필수 약관과 옵션 약관 모두 동의한 것으로 전송
            # "agreed_terms": [self.required_term.id, self.optional_term.id],
        }

    # def test_registration_success(self) -> None:
    #     """
    #     회원가입 성공 테스트:
    #     - 필수 약관에 동의하고, 유효한 비밀번호 등 올바른 데이터를 전송하면 회원가입이 완료됩니다.
    #     """
    #     response = self.client.post(self.registration_url, self.user_data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data["email"], self.user_data["email"])
    #
    # def test_registration_fail_missing_required_terms(self) -> None:
    #     """
    #     회원가입 실패 테스트:
    #     - 필수 약관에 동의하지 않은 경우 (필수 약관 누락) 회원가입이 실패해야 합니다.
    #     """
    #     user_data = self.user_data.copy()
    #     # 필수 약관을 제거하고 선택 약관만 전송
    #     user_data["agreed_terms"] = [self.optional_term.id]
    #     response = self.client.post(self.registration_url, user_data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # def test_registration_fail_invalid_agreed_terms_format(self) -> None:
    #     """
    #     회원가입 실패 테스트:
    #     - 약관 동의 데이터가 리스트 형식이 아니면 오류가 발생해야 합니다.
    #     """
    #     user_data = self.user_data.copy()
    #     user_data["agreed_terms"] = "not a list"  # 리스트가 아님
    #     response = self.client.post(self.registration_url, user_data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_fail_invalid_password(self) -> None:
        """
        회원가입 실패 테스트:
        - 유효하지 않은(예: 너무 약한) 비밀번호를 전송하면 회원가입이 실패해야 합니다.
        """
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
        """
        refresh token 재발급 성공 테스트:
        - 쿠키에 저장된 refresh token을 사용해 새로운 access token을 발급받을 수 있어야 합니다.
        """
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

    def test_refresh_token_fail_no_cookie(self) -> None:
        """
        refresh token 재발급 실패 테스트:
        - refresh token 쿠키가 없으면 에러 응답을 받아야 합니다.
        """
        self.client.cookies.clear()
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# 회원 탈퇴 API 테스트
class WithdrawTestCase(APITestCaseSetUp):
    def setUp(self) -> None:
        super().setUp()
        self.withdraw_url = reverse("withdraw")
        # 회원 탈퇴 시에도 refresh token을 블랙리스트에 추가해야 하므로 쿠키에 추가
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.client.cookies["refresh_token"] = self.refresh_token

    def test_withdraw_success(self) -> None:
        """
        회원 탈퇴 성공 테스트:
        - 회원 탈퇴 API 호출 시 사용자의 계정이 삭제(soft delete)되고, refresh token 쿠키가 삭제되어야 합니다.
        """
        response = self.client.post(self.withdraw_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "회원 탈퇴가 완료되었습니다.")
        # 응답 시 쿠키 삭제를 확인 (테스트 환경에 따라 쿠키 삭제 검증 방법은 다를 수 있음)
        self.assertNotIn("refresh_token", response.cookies)


# 마이페이지 - 회원정보 조회 및 수정 API 테스트
class MyPageTestCase(APITestCaseSetUp):
    def setUp(self) -> None:
        super().setUp()
        # 마이페이지 조회/수정 URL (urls.py에서 'user_detail' 혹은 'mypage'로 매핑되어 있다고 가정)
        self.mypage_url = reverse("mypage")

    def test_get_user_unauthorized(self) -> None:
        """
        인증 없이 회원정보 조회 시도:
        - 로그인이 되어 있지 않으면 401 Unauthorized 응답을 받아야 합니다.
        """
        self.client.logout()
        response = self.client.get(self.mypage_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_authorized(self) -> None:
        """
        인증 후 회원정보 조회:
        - 올바른 인증 정보가 있으면 회원정보가 정상적으로 조회되어야 합니다.
        """
        # APITestCaseSetUp에서 이미 인증 헤더를 설정했으므로 별도 로그인 불필요
        response = self.client.get(self.mypage_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], data["email"])

    def test_update_user_success(self) -> None:
        """
        회원정보 수정 테스트:
        - PUT 요청으로 일부 필드(예: name)를 수정할 수 있어야 합니다.
        - 요청 데이터에 사용자 id가 포함되어야 합니다.
        """
        update_data = {"id": self.user.id, "name": "Updated Name"}
        response = self.client.put(self.mypage_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), "Updated Name")


# 비밀번호 변경 API 테스트
class ChangePasswordTestCase(APITestCaseSetUp):
    def setUp(self) -> None:
        super().setUp()
        self.change_password_url = reverse("change_password")

    def test_change_password_success(self) -> None:
        """
        비밀번호 변경 성공 테스트:
        - 기존 비밀번호와 새 비밀번호를 전송하면 비밀번호가 성공적으로 변경되어야 합니다.
        """
        change_data = {"old_password": data["password"], "new_password": "NewStrongPassw0rd!"}
        response = self.client.post(self.change_password_url, change_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "비밀번호가 성공적으로 변경되었습니다.")
        # 변경 후 새 비밀번호로 인증이 가능한지 추가로 확인할 수 있음

    def test_change_password_fail_incorrect_old_password(self) -> None:
        """
        비밀번호 변경 실패 테스트:
        - 현재 비밀번호가 틀린 경우, 변경이 거부되어야 합니다.
        """
        change_data = {"old_password": "wrong_password", "new_password": "NewStrongPassw0rd!"}
        response = self.client.post(self.change_password_url, change_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# # 약관 리스트 조회 (TermsListView) API 테스트
# class TermsListTestCase(APITestCase):
#     def setUp(self) -> None:
#         self.terms_list_url = reverse('terms_list')
#         # 활성화된 약관 2개와 비활성 약관 1개 생성
#         Terms.objects.create(name="약관1", detail="내용1", is_required=True, is_active=True)
#         Terms.objects.create(name="약관2", detail="내용2", is_required=False, is_active=True)
#         Terms.objects.create(name="약관3", detail="내용3", is_required=True, is_active=False)
#
#     def test_terms_list(self) -> None:
#         """
#         약관 리스트 조회 테스트:
#         - GET 요청 시 활성화된 약관만 리스트로 반환되어야 합니다.
#         """
#         response = self.client.get(self.terms_list_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         # 활성화된 약관은 2개여야 함
#         self.assertEqual(len(response.data), 2)
#         # 각 약관에 필요한 필드가 포함되어 있는지 확인
#         for term in response.data:
#             self.assertIn("id", term)
#             self.assertIn("name", term)
#             self.assertIn("detail", term)
#             self.assertIn("is_required", term)
