from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class FoodView(APIView):
    def post(self, request):
        serializer = FoodSerializer(data=request.data)
        image_file = request.FILES.get('image', None)

        # Validate and save the serializer
        if serializer.is_valid():
            cat = request.data['category']
            cat = Category.objects.get(pk=cat)

            # Create the Food instance
            food = Food(**serializer.validated_data, category=cat)
            food.save()

            # Handle image file if present
            if image_file is not None:
                # Handle previous image removal
                if food.image:  # Check if food has an existing image before trying to remove it
                    try:
                        if os.path.isfile(food.image.path):
                            os.remove(food.image.path)
                    except Exception as e:
                        print(f"Error removing file: {e}")

                # Save the new image
                food.image = image_file
                food.save()  # Save the instance again with the new image

            # Return the response with serialized data
            return Response(FoodSerializer(food).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
