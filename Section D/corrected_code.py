"""
Section D — Step 2: Test & Debug (Without AI)
Refactored, robust, production-grade DRF implementation
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.db import transaction
from .models import Order


class OrderPlaceSerializer(serializers.ModelSerializer):
    """
    Serializer providing strict schema enforcement, automatic type coercion,
    and field-level validation according to DRF standards.
    """
    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'item', 'quantity', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate_customer_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Customer name cannot be empty or pure whitespace.")
        if len(cleaned) < 2:
            raise serializers.ValidationError("Customer name must be at least 2 characters.")
        return cleaned

    def validate_item(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Item name cannot be empty.")
        return cleaned

    def validate_quantity(self, value):
        # Prevent booleans from slipping through (in Python, True == 1)
        if isinstance(value, bool) or not isinstance(value, int):
            raise serializers.ValidationError("Quantity must be a valid integer.")
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer greater than zero.")
        return value


class PlaceOrderAPIView(APIView):
    """
    POST /api/orders/place/
    Production-ready endpoint leveraging Serializers and Atomic Transactions.
    """
    def post(self, request):
        serializer = OrderPlaceSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # Associate authenticated user if present, or persist customer_name
                user = request.user if request.user and request.user.is_authenticated else None
                saved_order = serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
