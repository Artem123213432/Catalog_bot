from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, Client, Product, OrderItem
from .serializers import OrderSerializer

class OrderCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        client_data = data.get('client')
        items_data = data.get('items', [])
        
        client, _ = Client.objects.get_or_create(
            phone=client_data['phone'],
            defaults={
                'name': client_data.get('name', ''),
                'address': client_data.get('address', '')
            }
        )
        
        order = Order.objects.create(client=client)
        
        for item in items_data:
            product = Product.objects.get(id=item['product_id'])
            OrderItem.objects.create(order=order, product=product, quantity=item.get('quantity', 1))
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED) 