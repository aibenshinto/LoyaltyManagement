from rest_framework import serializers
from .models import Customer, Cart

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "_all_"

class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity', 'product_name', 'product_price']