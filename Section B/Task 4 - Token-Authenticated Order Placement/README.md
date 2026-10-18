# Task 4: Token-Authenticated Order Placement

## Requirements & Implementation Summary
1. **Enabled DRF `TokenAuthentication`** in `settings.py` (`'rest_framework.authtoken'` in `INSTALLED_APPS` and configured authentication classes).
2. **Generated authentication tokens** for test users (`alice`, `bob`) via script/shell/admin.
3. **Created `PlaceOrderAPIView`** (`POST /api/my-orders/`) that uses `IsAuthenticated` permission and automatically saves `request.user` as the order owner.
4. **Created `GET /api/my-orders/` view** that returns only the orders belonging to the currently authenticated user (`request.user`).
5. **Returns HTTP 401 Unauthorized** with a clear, meaningful message for any unauthenticated request to either endpoint.

---

### 1. `settings.py` Configuration
```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework.authtoken',
    'api',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}
```

---

### 2. Token Generation via Django Shell / Python
```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user, created = User.objects.get_or_create(username='alice', email='alice@example.com')
user.set_password('password123')
user.save()

token, _ = Token.objects.get_or_create(user=user)
print("Alice Token:", token.key)
```

---

### 3. `models.py`
```python
from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    item = models.CharField(max_length=150)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
```

---

### 4. `serializers.py`
```python
from rest_framework import serializers
from .models import Order

class PlaceOrderSerializer(serializers.ModelSerializer):
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
```

---

### 5. `views.py`
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from .models import Order
from .serializers import OrderSerializer, PlaceOrderSerializer

class MyOrdersAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def handle_exception(self, exc):
        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            return Response(
                {
                    "error": "Unauthorized",
                    "detail": "Authentication credentials were not provided or token is invalid. Please provide a valid Authorization: Token <key> header."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().handle_exception(exc)

    def get(self, request):
        """
        Returns only orders belonging to request.user
        """
        orders = Order.objects.filter(user=request.user).order_by('-id')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Places order and assigns request.user as the owner
        """
        serializer = PlaceOrderSerializer(data=request.data)
        if serializer.is_valid():
            customer_name = serializer.validated_data.get('customer_name')
            if not customer_name:
                customer_name = request.user.get_full_name() or request.user.username

            order = serializer.save(
                user=request.user,
                customer_name=customer_name
            )
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

---

### 6. `urls.py`
```python
from django.urls import path
from .views import MyOrdersAPIView

urlpatterns = [
    path('api/my-orders/', MyOrdersAPIView.as_view(), name='my-orders'),
]
```

---

### Sample Postman Requests & Responses

#### A. Unauthenticated Request (HTTP 401 Unauthorized)
- **POST** `/api/my-orders/`
- **Headers:** *(No Authorization Header)*
- **Body:**
  ```json
  {
    "item": "Sushi Platter",
    "quantity": 2
  }
  ```
- **Response:**
  ```json
  // HTTP/1.1 401 Unauthorized
  {
    "error": "Unauthorized",
    "detail": "Authentication credentials were not provided or token is invalid. Please provide a valid Authorization: Token <key> header."
  }
  ```

#### B. Authenticated Order Placement (HTTP 201 Created)
- **POST** `/api/my-orders/`
- **Headers:**
  ```http
  Authorization: Token 425fe6988d35cf3f7fcab5657682273f34ffbadb
  Content-Type: application/json
  ```
- **Body:**
  ```json
  {
    "item": "Truffle Pasta",
    "quantity": 2
  }
  ```
- **Response:**
  ```json
  // HTTP/1.1 201 Created
  {
    "id": 13,
    "customer_name": "alice",
    "item": "Truffle Pasta",
    "quantity": 2,
    "status": "pending",
    "user": 1,
    "created_at": "2026-10-18T21:10:00Z"
  }
  ```

#### C. Authenticated Order History (HTTP 200 OK)
- **GET** `/api/my-orders/`
- **Headers:**
  ```http
  Authorization: Token 425fe6988d35cf3f7fcab5657682273f34ffbadb
  ```
- **Response:**
  ```json
  // HTTP/1.1 200 OK
  [
    {
      "id": 13,
      "customer_name": "alice",
      "item": "Truffle Pasta",
      "quantity": 2,
      "status": "pending",
      "user": 1,
      "created_at": "2026-10-18T21:10:00Z"
    }
  ]
  ```
*(Note: If Bob queries `/api/my-orders/` with his token, Alice's order is completely hidden and an empty array `[]` is returned).*
