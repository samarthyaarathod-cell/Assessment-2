from rest_framework import serializers
from decimal import Decimal
from .models import Category, MenuItem, Order


class CategorySerializer(serializers.ModelSerializer):
    """
    Task 1: Exposes id, name, and description.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class MenuItemSerializer(serializers.ModelSerializer):
    """
    Task 2: Validates price is greater than 0 and raises ValidationError if not.
    """
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'category', 'is_available']

    def validate_price(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Price must be greater than 0.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """
    Task 3: Serializer for Order listing, creation, and detail views.
    """
    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'item', 'quantity', 'status', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class PlaceOrderSerializer(serializers.ModelSerializer):
    """
    Task 4: Token-authenticated customer order placement.
    customer_name can optionally be inferred from request.user.
    """
    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'item', 'quantity', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']
        extra_kwargs = {
            'customer_name': {'required': False}
        }

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value
