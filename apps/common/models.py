from django.db import models

# Create your models here.
class BaseModel(models.Model):
	# auto_now_add 현재 데이터 생성 시간을 기준으로 생성 후 업데이트 시 수정되지 않음
	created_at = models.DateTimeField(auto_now_add=True)
	# auto_now 현재 데이터 생성 시간을 기준으로 생성 후 업데이트 시 현재 시간을 기준으로 수정됨
	updated_at = models.DateTimeField(auto_now=True)

	class Meta: # Meta는 Model의 동작 방식을 사용자 정의하는데 사용
		abstract = True # 추상화 True, 추상화된 클래스는 migrate 시 DB에 Table로 생성되지 않습니다.