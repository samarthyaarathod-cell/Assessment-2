from rest_framework import serializers
from decimal import Decimal
from .models import Category, MenuItem, Order


class CategorySerializer(serializers.ModelSerializer):
    """
    ModelSerializer for Category resource.
    Includes field-level validation for non-empty name.
    """
    menu_items_count = serializers.IntegerField(source='menu_items.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'menu_items_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        cleaned_name = value.strip()
        if not cleaned_name:
            raise serializers.ValidationError("Category name cannot be blank or empty.")
        if len(cleaned_name) < 2:
            raise serializers.ValidationError("Category name must be at least 2 characters long.")
        return cleaned_name


class MenuItemSerializer(serializers.ModelSerializer):
    """
    ModelSerializer for MenuItem resource.
    Includes field-level validation for:
      - Price greater than 0.
      - Non-empty name.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'category', 'category_name', 'is_available', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        cleaned_name = value.strip()
        if not cleaned_name:
            raise serializers.ValidationError("Menu item name cannot be empty or whitespace.")
        if len(cleaned_name) < 2:
            raise serializers.ValidationError("Menu item name must be at least 2 characters long.")
        return cleaned_name

    def validate_price(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Price must be strictly greater than 0.")
        if value > Decimal('9999.99'):
            raise serializers.ValidationError("Price exceeds maximum permitted limit ($9999.99).")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """
    ModelSerializer for Order resource.
    Includes field-level validation for:
      - Quantity greater than or equal to 1.
      - Non-empty item name.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_username',
            'customer_name',
            'item',
            'quantity',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_username', 'created_at', 'updated_at']
        extra_kwargs = {
            'customer_name': {'required': False}
        }

    def validate_item(self, value):
        cleaned_item = value.strip()
        if not cleaned_item:
            raise serializers.ValidationError("Item name cannot be empty.")
        return cleaned_item

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be greater than or equal to 1.")
        return value
