from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from Account.models import Account
from Address.models import Address
from Address.serializers import AddressSerializer


class AddressListAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = request.data.copy()  # Copy to avoid modifying the original request.data
        uuid = data.get('uuid')
        if type(uuid) is str:
            try:
                address = Address.objects.get(uuid=uuid)
                data['created_by'] = request.user.phone
                serializer = AddressSerializer(data=data, instance=address)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                else:
                    print(serializer.errors)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            except Address.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            account = Account.objects.get(phone=request.user.phone)
            data['created_by'] = request.user.phone  # Add additional data like the user's ID
            serializer = AddressSerializer(data=data)
            if serializer.is_valid():
                instance = serializer.save()
                account.addresses.add(instance)
                account.save()
                return Response(serializer.data)
            else:
                print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)
