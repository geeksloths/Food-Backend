from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from Comment.forms import CommentForm
from Comment.models import Comment
from Comment.serializers import CommentSerializer


class CommentAPIList(APIView):
    def get(self, request, uuid):
        comments = Comment.objects.filter(comment_for=uuid).order_by('-published_at')
        serializer = CommentSerializer(comments, many=True)
        return Response({'comments': serializer.data})

    def post(self, request, uuid):
        data = request.data
        form = CommentForm(data)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.comment_from = request.user
            instance.comment_for = uuid
            instance.save()
            serializer = CommentSerializer(instance)
            return Response({'comments': [serializer.data]})
        else:
            print(form.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)
