from django.shortcuts import render
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from Category.models import Category
from Category.serializers import CategorySerializer


# Create your views here.
class ListApi(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        cats = Category.objects.filter(created_by=request.user)
        return Response({"categories": CategorySerializer(cats, many=True).data})
