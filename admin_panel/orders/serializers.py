from rest_framework import serializers
from .models import Order, OrderItem, Client, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'phone', 'address']

class OrderSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'client', 'items', 'created_at'] 