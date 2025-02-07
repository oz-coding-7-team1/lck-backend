from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Terms, TermsAgreement

User = get_user_model()


class UserAPITests(APITestCase):
    def setUp(self) -> None:
        # 테스트용 약관 데이터 생성 (필수 약관 2개, 선택 약관 1개)
        self.required_term1 = Terms.objects.create(
            name="필수 약관 1",
            detail="필수 약관 내용 1",
            is_active=True,
            is_required=True,
        )
        self.required_term2 = Terms.objects.create(
            name="필수 약관 2",
            detail="필수 약관 내용 2",
            is_active=True,
            is_required=True,
        )
        self.optional_term = Terms.objects.create(
            name="선택 약관",
            detail="선택 약관 내용",
            is_active=True,
            is_required=False,
        )

        self.client = APIClient()
        # 테스트에서 사용할 URL.
        self.register_url = "/api/v1/signup/"
        self.login_url = "/api/v1/login/"
        self.mypage_url = "/api/v1/user/mypage/"
        self.logout_url = "/api/v1/logout/"
        self.change_password_url = "/api/v1/user/password/"
        self.terms_url = "/api/v1/terms/"

    def test_user_registration_missing_required_terms(self) -> None:
        """
        필수 약관에 동의하지 않았을 때 회원가입 실패를 확인하는 테스트
        """
        data = {
            "email": "test@example.com",
            "nickname": "testuser",
            "password": "StrongPassword123!",
            # 필수 약관은 포함하지 않고 선택 약관만 동의한 경우
            "agreed_terms": [self.optional_term.id],
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 응답 데이터에 '필수 약관에 모두 동의해야 합니다.'라는 메시지가 포함되어 있어야 함
        self.assertIn("필수 약관에 모두 동의해야 합니다", str(response.data))

    def test_user_registration_success(self) -> None:
        """
        필수 약관에 모두 동의했을 때 회원가입이 성공하는지 확인하는 테스트
        """
        data = {
            "email": "test2@example.com",
            "nickname": "testuser2",
            "password": "StrongPassword123!",
            # 필수 약관 2개에 동의
            "agreed_terms": [self.required_term1.id, self.required_term2.id],
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 생성된 사용자가 데이터베이스에 존재하는지 확인
        user = User.objects.get(email="test2@example.com")
        self.assertIsNotNone(user)
        # 약관 동의 기록이 제대로 생성되었는지 확인 (필수 약관 2개)
        agreements = TermsAgreement.objects.filter(user=user)
        self.assertEqual(agreements.count(), 2)

    def test_user_login_success(self) -> None:
        """
        올바른 이메일과 비밀번호로 로그인 시 JWT 토큰이 발급되는지 테스트
        """
        # 테스트용 사용자 생성 (create_user 내부에서 set_password를 호출함)
        user = User.objects.create_user(email="login@example.com", password="TestPassword123!", nickname="loginuser")
        data = {
            "email": "login@example.com",
            "password": "TestPassword123!",
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_failure(self) -> None:
        """
        잘못된 인증 정보로 로그인 시 실패하는지 테스트
        """
        data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword!",
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mypage_view_authenticated(self) -> None:
        """
        로그인한 사용자가 마이페이지 조회 시 올바른 사용자 정보를 받는지 테스트
        """
        user = User.objects.create_user(email="mypage@example.com", password="TestPassword123!", nickname="mypageuser")
        self.client.force_authenticate(user=user)
        response = self.client.get(self.mypage_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("email"), "mypage@example.com")

    def test_logout_view(self) -> None:
        """
        로그인 후 로그아웃 API를 호출하여 로그아웃이 정상 동작하는지 테스트
        """
        user = User.objects.create_user(email="logout@example.com", password="TestPassword123!", nickname="logoutuser")
        # 로그인하여 토큰 발급
        login_response = self.client.post(
            self.login_url, {"email": "logout@example.com", "password": "TestPassword123!"}, format="json"
        )
        refresh_token = login_response.data.get("refresh")
        self.client.force_authenticate(user=user)
        data = {"refresh": refresh_token}
        response = self.client.post(self.logout_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_change_password_success(self) -> None:
        """
        올바른 현재 비밀번호를 입력했을 때 비밀번호 변경이 성공하는지 테스트
        """
        user = User.objects.create_user(
            email="changepw@example.com", password="OldPassword123!", nickname="changepwuser"
        )
        self.client.force_authenticate(user=user)
        data = {"old_password": "OldPassword123!", "new_password": "NewPassword123!"}
        response = self.client.post(self.change_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 비밀번호 변경 후 새 비밀번호로 로그인 테스트
        self.client.logout()
        login_response = self.client.post(
            self.login_url, {"email": "changepw@example.com", "password": "NewPassword123!"}, format="json"
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_change_password_failure_wrong_old_password(self) -> None:
        """
        현재 비밀번호가 틀린 경우 비밀번호 변경이 실패하는지 테스트
        """
        user = User.objects.create_user(
            email="changepw2@example.com", password="OldPassword123!", nickname="changepwuser2"
        )
        self.client.force_authenticate(user=user)
        data = {"old_password": "WrongOldPassword!", "new_password": "NewPassword123!"}
        response = self.client.post(self.change_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_terms_list_view(self) -> None:
        """
        약관 리스트 조회 API가 정상적으로 활성 약관 정보를 반환하는지 테스트
        """
        response = self.client.get(self.terms_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 반환된 데이터가 리스트 형태인지 확인
        self.assertIsInstance(response.data, list)
        if response.data:
            term = response.data[0]
            self.assertIn("id", term)
            self.assertIn("name", term)
            self.assertIn("detail", term)
            self.assertIn("is_required", term)
