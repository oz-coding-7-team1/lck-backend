from typing import Any, Dict, List

from rest_framework import serializers

from .models import PlayerComment, PlayerPost, TeamComment, TeamPost


# 팀 게시글에 달린 댓글을 직렬화
class TeamCommentSerializer(serializers.ModelSerializer[TeamComment]):
    replies = serializers.SerializerMethodField()  # 대댓글 처리를 위한 필드

    class Meta:
        model = TeamComment
        fields = ["id", "user", "content", "parent", "created_at", "replies"]

    def get_replies(self, obj: TeamComment) -> List[Dict[str, Any]]:
        qs = obj.replies.all()
        return TeamCommentSerializer(qs, many=True).data  # type: ignore


# 팀 게시글과 연결된 댓글을 포함한 전체 데이터 직렬화
class TeamPostSerializer(serializers.ModelSerializer[TeamPost]):
    comments = TeamCommentSerializer(many=True, read_only=True)  # 댓글 목록 포함

    class Meta:
        model = TeamPost
        fields = ["id", "team", "user", "title", "content", "created_at", "updated_at", "comments"]


# 선수 게시글에 달린 댓글을 직렬화
class PlayerCommentSerializer(serializers.ModelSerializer[PlayerComment]):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = PlayerComment
        fields = ["id", "user", "content", "parent", "created_at", "replies"]

    def get_replies(self, obj: PlayerComment) -> List[Dict[str, Any]]:
        qs = obj.replies.all()
        return PlayerCommentSerializer(qs, many=True).data  # type: ignore


# 선수 게시글과 연결된 댓글을 포함한 전체 데이터 직렬화
class PlayerPostSerializer(serializers.ModelSerializer[PlayerPost]):
    comments = PlayerCommentSerializer(many=True, read_only=True)

    class Meta:
        model = PlayerPost
        fields = ["id", "player", "user", "title", "content", "created_at", "updated_at", "comments"]
