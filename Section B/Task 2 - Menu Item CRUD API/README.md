# Task 2: Menu Item CRUD API

## Requirements & Implementation Summary
1. **MenuItem model created** with:
   - `name` (`CharField`)
   - `price` (`DecimalField`)
   - `category` (`ForeignKey` to Category)
   - `is_available` (`BooleanField`)
2. **MenuItemSerializer** created using `ModelSerializer`:
   - Validates `price > 0`, raising `ValidationError` if price is 0 or negative.
3. **Endpoints implemented using `APIView`**:
   - `GET /api/menu-items/` (List all items, HTTP 200)
   - `POST /api/menu-items/` (Create new item, HTTP 201 on success, HTTP 400 on validation failure)
   - `GET /api/menu-items/<id>/` (Retrieve single item, HTTP 200 or HTTP 404)
   - `PUT /api/menu-items/<id>/` (Update item, HTTP 200, HTTP 400 on error, HTTP 404 if not found)
   - `DELETE /api/menu-items/<id>/` (Delete item, HTTP 204 or HTTP 404)
4. Returns correct HTTP status codes:
   - HTTP 201 for successful creation.
   - HTTP 400 for validation failures.
   - HTTP 404 when item is not found.

---

### 1. `models.py`
```python
from django.db import models
from .models import Category

class MenuItem(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"
```

---

### 2. `serializers.py`
```python
from rest_framework import serializers
from decimal import Decimal
from .models import MenuItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'category', 'is_available']

    def validate_price(self, value):
        """
        Validates price is strictly greater than 0.
        """
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
```

---

### 3. `views.py`
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MenuItem
from .serializers import MenuItemSerializer

class MenuItemListCreateAPIView(APIView):
    def get(self, request):
        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuItemDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            return None

    def get(self, request, pk):
        item = self.get_object(pk)
        if item is None:
            return Response({"error": f"MenuItem with id {pk} was not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MenuItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        item = self.get_object(pk)
        if item is None:
            return Response({"error": f"MenuItem with id {pk} was not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MenuItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = self.get_object(pk)
        if item is None:
            return Response({"error": f"MenuItem with id {pk} was not found."}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"message": f"MenuItem {pk} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
```

---

### 4. `urls.py`
```python
from django.urls import path
from .views import MenuItemListCreateAPIView, MenuItemDetailAPIView

urlpatterns = [
    path('api/menu-items/', MenuItemListCreateAPIView.as_view(), name='menuitem-list-create'),
    path('api/menu-items/<int:pk>/', MenuItemDetailAPIView.as_view(), name='menuitem-detail'),
]
```

---

### Sample Postman Requests & Responses

#### A. Successful Creation (HTTP 201)
- **POST** `/api/menu-items/`
- **Body:**
  ```json
  {
    "name": "Margherita Pizza",
    "price": "12.99",
    "category": 1,
    "is_available": true
  }
  ```
- **Response:**
  ```json
  // HTTP/1.1 201 Created
  {
    "id": 1,
    "name": "Margherita Pizza",
    "price": "12.99",
    "category": 1,
    "is_available": true
  }
  ```

#### B. Validation Failure (HTTP 400)
- **POST** `/api/menu-items/`
- **Body:**
  ```json
  {
    "name": "Invalid Dish",
    "price": "-4.50",
    "category": 1,
    "is_available": true
  }
  ```
- **Response:**
  ```json
  // HTTP/1.1 400 Bad Request
  {
    "price": [
      "Price must be greater than 0."
    ]
  }
  ```

#### C. Item Not Found (HTTP 404)
- **GET** `/api/menu-items/999/`
- **Response:**
  ```json
  // HTTP/1.1 404 Not Found
  {
    "error": "MenuItem with id 999 was not found."
  }
  ```
