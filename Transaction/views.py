import json
from datetime import datetime
from functools import reduce

from django.db.models import QuerySet
from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from Account.models import Account
from Food.forms import FoodForm
from Food.models import Food
from Restaurant.models import Restaurant
from Transaction.forms import TransactionForm, OrderForm
from Transaction.models import TransactionModel, OrderModel
from Transaction.serializers import TransactionSerializer


class MyQuerySet(QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self._result_cache = []

    def _clone(self):
        clone = super()._clone()
        clone._result_cache = self._result_cache[:]


def querydict_to_nested_dict(query_dict):
    result = {}

    for key, value in query_dict.lists():  # Use lists() to handle multiple values
        current = result
        keys = key.replace(']', '').split('[')  # Parse the keys

        for k in keys[:-1]:
            # Create nested dictionaries as needed
            if k not in current:
                current[k] = {}
            current = current[k]

            # The last key is where we set the value
        current[keys[-1]] = value[0]  # Store the first value

    return result


def get_related_transactions(user: Account):
    transactions = TransactionModel.objects.all()
    related_transactions = []
    for transaction in transactions:
        add_check = is_related(transaction, user)
        if add_check:
            related_transactions.append(transaction)
    return related_transactions


def is_related(transaction: TransactionModel, user: Account):
    add_check = False
    orders = OrderModel.objects.filter(transaction=transaction)
    for order in orders:
        if order.created_by.phone == user.phone or order.restaurant.owner_account.phone == user.phone:
            add_check = True
    return add_check


def list_to_queryset(model, object_list):
    queryset = MyQuerySet(model=model, query=model.objects.all().query)
    queryset._result_cache = object_list
    return queryset


class TransactionListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        status_param = request.query_params.get('status', None)
        transactions = get_related_transactions(request.user)
        new_queryset = list_to_queryset(TransactionModel, transactions)
        if status_param:
            list_status = str(status_param).split(',')
            new_queryset = new_queryset.filter(status__in=list_status)
        # new_queryset = new_queryset.order_by('-paid_time')
        return Response(
            {'transactions': TransactionSerializer(new_queryset, many=True, context={'user': request.user}).data})

    def post(self, request):
        try:
            form = TransactionForm(request.data)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.created_by = request.user
                paid_time = datetime.utcnow()
                instance.paid_time = paid_time
                instance.save()
                orders = request.data.get('orders')
                orders = json.loads(orders)
                orders_list = []
                print(request.data)
                print(f'orders: {orders}')
                for order in orders:
                    order['extras'] = json.loads(order['extras'])
                    order['instructions'] = json.loads(order['instructions'])
                    order['sizes'] = json.loads(order['sizes'])
                    order_form = OrderForm(order)
                    if order_form.is_valid():
                        res = Restaurant.objects.get(uuid=order['restaurant'])
                        food = Food.objects.get(uuid=order['food_uuid'])
                        order_instance = order_form.save(commit=False)
                        order_instance.created_by = request.user
                        order_instance.restaurant = res
                        order_instance.food = food
                        order_instance.save()
                        orders_list.append(order_instance)
                    else:
                        print("order error")
                        print(order_form.errors)
                instance.orders.set(orders_list)
                transactions = TransactionModel.objects.filter(created_by=request.user)
                with open("json.json", "w", encoding="utf8") as f:
                    f.write(json.dumps({"transactions": TransactionSerializer(transactions, many=True,
                                                                              context={'user': request.user}).data}))
                return Response({"transactions": TransactionSerializer(transactions, many=True,
                                                                       context={'user': request.user}).data})
            else:
                print(form.errors)
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, serial):
        print('hellow')
        try:
            serial = int(serial)
            transaction = TransactionModel.objects.get(serial=serial)
            for order in OrderModel.objects.filter(transaction=transaction):
                order.delete()
            transaction.delete()
            return Response(TransactionSerializer(transaction, context={'user': request.user}).data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TransactionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, serial):
        transactions = get_related_transactions(request.user)
        serial = int(serial) if serial is not None else None
        serials = [t.serial for t in transactions]
        if serial is not None and serial in serials:
            try:
                transaction = TransactionModel.objects.get(serial=serial)
                return Response({'transactions': [
                    TransactionSerializer(transaction, context={'big': True, 'user': request.user}).data]})
            except TransactionModel.DoesNotExist as e:
                return Response({'transactions': []}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'transactions': []}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, serial):
        if serial is not None:
            try:
                transaction = TransactionModel.objects.get(serial=serial)
                serializer = TransactionSerializer(transaction, data=request.data, context={'user': request.user},
                                                   partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except TransactionModel.DoesNotExist:
                return Response({'error': 'Transaction not found!'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TransactionVerification(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, serial, code):
        try:
            transaction = TransactionModel.objects.get(serial=serial)
            related = is_related(transaction, request.user)
            if related:
                code = int(code)
                if code == transaction.delivery_code:
                    transaction.status = "CO"
                    transaction.save()
                    return Response({'transactions': [
                        TransactionSerializer(transaction, context={'big': True, 'user': request.user}).data]})
                return Response({'error', 'Wrong Code!'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error', 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
        except TransactionModel.DoesNotExist as e:
            return Response({'error': 'Transaction not found!'}, status=status.HTTP_404_NOT_FOUND)

