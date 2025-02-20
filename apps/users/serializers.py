from typing import Any

from rest_framework import serializers

from .models import Terms, TermsAgreement, User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ("id", "email", "nickname", "is_active", "is_staff", "is_superuser")


class MypageSerializer(serializers.ModelSerializer[User]):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "nickname", "profile_image_url")

    def get_profile_image_url(self, obj: User) -> str | None:
        image = obj.user_images.first()
        if image:
            return image.image_url
        return None


class TermsSerializer(serializers.ModelSerializer[Terms]):
    class Meta:
        model = Terms
        fields = ("id", "name", "detail", "is_active", "is_required")


class TermsAgreementSerializer(serializers.ModelSerializer[TermsAgreement]):
    terms_detail = TermsSerializer(source="terms", read_only=True)

    class Meta:
        model = TermsAgreement
        fields = ("id", "terms", "terms_detail", "is_active")
        extra_kwargs = {
            "terms": {"write_only": True},
        }


class SignupSerializer(serializers.ModelSerializer[User]):
    terms_agreements = TermsAgreementSerializer(many=True, write_only=True)

    class Meta:
        model = User
        fields = ("email", "nickname", "password", "terms_agreements")

    def validate_terms_agreements(self, value: Any) -> Any:
        # filter(): 조건에 맞는 쿼리셋을 반환
        # .all() 을 붙여도 동일한 결과를 내지만 중복된 호출이므로 filter(is_active=True) 만 사용
        # 데이터를 집합 자료형으로 변환 / 중복을 제거하고 수학적 집합 연산을 효율적으로 수행할 수 있어서 존재 여부를 빠르게 확인 가능
        required_terms = set(Terms.objects.filter(is_required=True, is_active=True).values_list("id", flat=True))
        agreed_terms = set()
        for item in value:
            if item.get("is_active"):
                term_obj = item.get("terms")
                # 만약 term_obj 가 Terms 인스턴스라면 id 를 추출, 아니면 그대로 사용
                if hasattr(term_obj, "id"):
                    agreed_terms.add(term_obj.id)
                else:
                    agreed_terms.add(term_obj)
        if required_terms - agreed_terms:
            raise serializers.ValidationError("회원가입을 위해서는 모든 필수 약관에 동의해야 합니다.")
        return value

    def create(self, validated_data: Any) -> User:
        terms_data = validated_data.pop("terms_agreements")
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        for term in terms_data:
            TermsAgreement.objects.create(user=user, **term)
        return user


class LoginSerializer(serializers.Serializer[None]):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenResponseSerializer(serializers.Serializer[None]):
    access_token = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer[User]):
    old_password = serializers.CharField(help_text="현재 비밀번호", write_only=True)
    new_password = serializers.CharField(help_text="새 비밀번호", write_only=True)
