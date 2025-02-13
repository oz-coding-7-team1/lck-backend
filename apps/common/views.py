from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.players.models import Player
from apps.teams.models import Team
from drf_spectacular.utils import extend_schema, OpenApiParameter
from apps.players.serializers import PlayerSerializer
from apps.teams.serializers import TeamSerializer

# Create your views here.
class TagSearchView(APIView):
	"""태그 기반으로 Player와 Team을 검색"""
	permission_classes = [AllowAny]
	
	@extend_schema(
		summary="태그로 검색",
		description="쿼리문자열로 검색합니다.",
		parameters=[
			OpenApiParameter("search", type=str, description="검색할 태그")
		],
		responses={200: "검색 결과 반환"}
	)
	def get(self, request):
		# URL의 쿼리 파라미터(?search=검색어)에서 검색어를 가져온다
		# ex) GET /api/v1/search/?search=페이커
		query = request.GET.get("search", "").strip()

		# 검색어가 입력되지 않았을 때
		if not query:
			return Response({"error": "검색어를 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

		# icontains: query의 대소문자 구분 X / distinct: 중복된 결과 방지
		players = Player.objects.filter(tags__name__icontains=query).distinct()
		teams = Team.objects.filter(tags__name__icontains=query).distinct()
		
		player_serializer = PlayerSerializer(players, many=True)
		team_serializer = TeamSerializer(teams, many=True)
		
		return Response(
			{
				"players": player_serializer.data,
				"teams": team_serializer.data,
			},
			status=status.HTTP_200_OK,
		)