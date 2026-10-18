# Task 1: Food Category Listing API

## Requirements & Implementation Summary
1. **Category model created** with:
   - `name`: `CharField(max_length=100)`
   - `description`: `TextField()`
2. **CategorySerializer** created using `ModelSerializer` exposing `id`, `name`, and `description`.
3. **ListAPIView endpoint** mapped to `/api/categories/` and registered in `urls.py`.
4. Returns all categories as a JSON array with HTTP 200.

---

### 1. `models.py`
```python
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
```

---

### 2. `serializers.py`
```python
from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
```

---

### 3. `views.py`
```python
from rest_framework import generics
from .models import Category
from .serializers import CategorySerializer

class CategoryListAPIView(generics.ListAPIView):
    """
    Read-only DRF endpoint returning all food categories as a JSON response.
    Mapped to /api/categories/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None  # Ensure raw unpaginated JSON array as specified
```

---

### 4. `urls.py`
```python
from django.urls import path
from .views import CategoryListAPIView

urlpatterns = [
    path('api/categories/', CategoryListAPIView.as_view(), name='category-list'),
]
```

---

### Sample Postman Request & Response

#### Request
```http
GET /api/categories/ HTTP/1.1
Host: 127.0.0.1:8000
Accept: application/json
```

#### Response
```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "id": 1,
    "name": "Pizza",
    "description": "Artisan wood-fired pizzas"
  },
  {
    "id": 2,
    "name": "Burgers",
    "description": "Juicy gourmet burgers and fries"
  },
  {
    "id": 3,
    "name": "Desserts",
    "description": "Cakes, ice creams, and sweet delights"
  }
]
```
