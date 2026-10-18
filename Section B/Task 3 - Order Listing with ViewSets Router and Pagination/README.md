# Task 3: Order Listing with ViewSets, Router, and Pagination

## Requirements & Implementation Summary
1. **Order model created** with:
   - `customer_name`: `CharField(max_length=100)`
   - `item`: `CharField(max_length=150)`
   - `quantity`: `IntegerField()`
   - `status`: `CharField` with choices: `pending`, `confirmed`, `delivered`.
2. **Converted Order API to `ModelViewSet`** and registered with `DefaultRouter`.
   - Router auto-generates all CRUD URLs under `/api/orders/`.
3. **Configured `PageNumberPagination`** with `PAGE_SIZE = 5` and applied to Order ViewSet.
4. **Supports filtering orders by status** using a query parameter (e.g., `/api/orders/?status=pending`) via the `get_queryset()` method.

---

### 1. `models.py`
```python
from django.db import models

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
    )

    customer_name = models.CharField(max_length=100)
    item = models.CharField(max_length=150)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.item} ({self.status})"

    class Meta:
        ordering = ['-id']
```

---

### 2. `serializers.py`
```python
from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'item', 'quantity', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value
```

---

### 3. `views.py`
```python
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import Order
from .serializers import OrderSerializer

class OrderPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50

class OrderViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet registered with DefaultRouter.
    Automatically provides list, create, retrieve, update, destroy.
    Includes page_size = 5 pagination.
    Filters by status query parameter via get_queryset().
    """
    serializer_class = OrderSerializer
    pagination_class = OrderPagination

    def get_queryset(self):
        queryset = Order.objects.all().order_by('-id')
        status_param = self.request.query_params.get('status', None)
        if status_param is not None:
            queryset = queryset.filter(status__iexact=status_param.strip())
        return queryset
```

---

### 4. `urls.py`
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

---

### 5. `settings.py` (Pagination Config)
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
}
```

---

### Sample Postman Requests & Responses

#### A. Paginated Listing (HTTP 200)
- **GET** `/api/orders/`
- **Response:**
  ```json
  {
    "count": 12,
    "next": "http://127.0.0.1:8000/api/orders/?page=2",
    "previous": null,
    "results": [
      {
        "id": 12,
        "customer_name": "Customer 12",
        "item": "Item #12",
        "quantity": 12,
        "status": "delivered",
        "created_at": "2026-10-18T21:09:00Z"
      },
      {
        "id": 11,
        "customer_name": "Customer 11",
        "item": "Item #11",
        "quantity": 11,
        "status": "pending",
        "created_at": "2026-10-18T21:09:00Z"
      },
      {
        "id": 10,
        "customer_name": "Customer 10",
        "item": "Item #10",
        "quantity": 10,
        "status": "delivered",
        "created_at": "2026-10-18T21:09:00Z"
      },
      {
        "id": 9,
        "customer_name": "Customer 9",
        "item": "Item #9",
        "quantity": 9,
        "status": "pending",
        "created_at": "2026-10-18T21:09:00Z"
      },
      {
        "id": 8,
        "customer_name": "Customer 8",
        "item": "Item #8",
        "quantity": 8,
        "status": "delivered",
        "created_at": "2026-10-18T21:09:00Z"
      }
    ]
  }
  ```

#### B. Filtered by Status (HTTP 200)
- **GET** `/api/orders/?status=pending`
- **Response:**
  ```json
  {
    "count": 6,
    "next": "http://127.0.0.1:8000/api/orders/?page=2&status=pending",
    "previous": null,
    "results": [
      {
        "id": 11,
        "customer_name": "Customer 11",
        "item": "Item #11",
        "quantity": 11,
        "status": "pending",
        "created_at": "2026-10-18T21:09:00Z"
      },
      {
        "id": 9,
        "customer_name": "Customer 9",
        "item": "Item #9",
        "quantity": 9,
        "status": "pending",
        "created_at": "2026-10-18T21:09:00Z"
      }
    ]
  }
  ```
