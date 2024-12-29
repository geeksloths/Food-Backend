import math
from functools import reduce

from rest_framework import serializers

from Comment.models import Comment
from Extras.serializers import ExtraSerializer
from Food.models import Food, SizeModel
from Instruction.serializers import InstructionSerializer
from Restaurant.serializers import RestaurantSerializer
from food_backend.env import Env

SERVER = Env().get_server()


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeModel
        fields = "__all__"


class FoodSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image')
    sizes = serializers.SerializerMethodField('get_sizes')
    restaurant = serializers.SerializerMethodField('get_restaurant')
    comments_count = serializers.SerializerMethodField('get_comments_count')
    rating = serializers.SerializerMethodField('get_rating')
    rating_count = serializers.SerializerMethodField('get_rating_count')

    class Meta:
        model = Food
        fields = [
            "uuid",
            "name",
            'image',
            "price",
            "details",
            "preparation_time",
            "rating",
            "sizes",
            "restaurant",
            'comments_count',
            'rating_count',
            "category",
        ]

    def get_image(self, food):
        if food.image and food.image is None:
            return None
        else:
            return SERVER + food.image.url

    def get_comments_count(self, res):
        comments = Comment.objects.filter(comment_for=res.uuid)
        return len(comments)

    def get_rating(self, res):
        comments = Comment.objects.filter(comment_for=res.uuid)
        integer_values = [obj.rating for obj in comments]
        total_sum = reduce(lambda x, y: x + y, integer_values, 0)
        mean_val = (math.ceil((total_sum / len(comments)) * 10) / 10) if len(comments) > 0 else 0
        return str(mean_val)

    def get_rating_count(self, res):
        comments = Comment.objects.filter(comment_for=res.uuid)
        length = [obj.rating for obj in comments if obj.rating != 0]
        return len(length)

    def get_sizes(self, food):
        sizes = SizeModel.objects.filter(food=food)
        return SizeSerializer(sizes, many=True).data

    def get_restaurant(self, food):
        big = self.context.get('use_res', True)
        if big:
            return RestaurantSerializer(food.restaurant).data
        return food.restaurant.uuid
