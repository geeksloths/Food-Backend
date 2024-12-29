import json

from django.http import HttpResponse
from django.shortcuts import render
from fuzzywuzzy import fuzz
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from Food.models import Food
from Food.serializers import FoodSerializer
from Restaurant.models import Restaurant
from Restaurant.serializers import RestaurantSerializer
from Transaction.models import TransactionModel


# Create your views here.
class FixAPI(APIView):
    def get(self, request):
        transactions = TransactionModel.objects.all()
        for t in transactions:
            address = t.created_by.addresses.first()
            if address:
                t.latitude = address.latitude
                t.longitude = address.longitude
                t.brief_address = address.brief_address
                t.phone = t.created_by.phone
                t.save()
        return Response([])


def check(request):
    return HttpResponse(json.dumps(True))


class SearchAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', None)
        print(f"query is {query}")
        if query:
            foods = Food.objects.all()
            restaurants = Restaurant.objects.all()
            results = []

            for food in foods:
                ratio = fuzz.ratio(query, food.name)
                if ratio >= 30:
                    results.append((food, ratio, 'food'))

            for restaurant in restaurants:
                ratio = fuzz.ratio(query, restaurant.name)
                print(f"{restaurant.name} ratio for {query} is {ratio}")
                if ratio >= 30:
                    results.append((restaurant, ratio, 'restaurant'))

            results.sort(key=lambda x: x[1], reverse=True)

            return Response({
                'results': [
                    {'type': 'food', 'data': FoodSerializer(result[0]).data} if result[2] == 'food' else {
                        'type': 'restaurant',
                        'data': RestaurantSerializer(result[0]).data}
                    for result in results
                ]
            }, status=status.HTTP_200_OK)
        return Response({'error': 'No query parameter provided'}, status=status.HTTP_400_BAD_REQUEST)
