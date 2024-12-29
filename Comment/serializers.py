from rest_framework import serializers

from Account.serializers import AccountSerializer
from Comment.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    comment_for = serializers.SerializerMethodField()
    comment_from = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'uuid',
            'title',
            'content',
            'comment_for',
            'comment_from',
            'published_at',
            'isVerified',
            'rating',
        ]

    def get_comment_for(self, obj):
        # You can customize this to return a more meaningful representation
        return AccountSerializer(obj.comment_for).data

    def get_comment_from(self, obj):
        # Assuming you want to return the username or a specific field from the Account model
        return AccountSerializer(obj.comment_from).data