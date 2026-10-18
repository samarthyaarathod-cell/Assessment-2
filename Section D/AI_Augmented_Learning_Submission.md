# Section D — AI-Augmented Learning

**Assessment Code:** M5-A1  
**Topic:** AI-Assisted Development, Testing, and Code Hardening  

---

## Step 1: Build with AI

### 1. Exact AI Prompt(s)

```text
Act as a Senior Django REST Framework developer. I need an API endpoint in Django REST Framework to place food orders:
1. Implement a POST /api/orders/place/ endpoint using DRF APIView that accepts `customer_name`, `item`, and `quantity` in the JSON request body.
2. Validate that `quantity` is a positive integer and return a JSON error response with HTTP 400 Bad Request if validation fails.
3. Save the order to the database using an Order model and return the saved order details (including the auto-generated `id`) with HTTP 201 Created on success.
4. Show me the complete view and URL pattern.
```

---

### 2. Original AI Code (Unmodified Output)

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order

class PlaceOrderAPIView(APIView):
    """
    POST /api/orders/place/
    Accepts customer_name, item, and quantity in request body.
    """
    def post(self, request):
        customer_name = request.data.get('customer_name')
        item = request.data.get('item')
        quantity = request.data.get('quantity')

        # Validate that quantity is a positive integer
        if not isinstance(quantity, int) or quantity <= 0:
            return Response(
                {"error": "Quantity must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save order directly to the database
        order = Order.objects.create(
            customer_name=customer_name,
            item=item,
            quantity=quantity
        )

        # Return saved order details with auto-generated ID
        return Response({
            "id": order.id,
            "customer_name": order.customer_name,
            "item": order.item,
            "quantity": order.quantity,
            "status": order.status
        }, status=status.HTTP_201_CREATED)
```

---

## Postman End-to-End Test Demonstration

### Demonstration A: Successful Request (HTTP 201 Created)
- **Endpoint:** `POST http://127.0.0.1:8000/api/orders/place/`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "customer_name": "Michael Scott",
    "item": "Chicken Fettuccine Alfredo",
    "quantity": 3
  }
  ```

#### Postman Screenshot Simulation:
```
+----------------------------------------------------------------------------------------------------+
| POST  http://127.0.0.1:8000/api/orders/place/                                   [Send]             |
+----------------------------------------------------------------------------------------------------+
| Headers: Content-Type: application/json                                                            |
| Body (raw JSON):                                                                                   |
| {                                                                                                  |
|   "customer_name": "Michael Scott",                                                                |
|   "item": "Chicken Fettuccine Alfredo",                                                            |
|   "quantity": 3                                                                                    |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
| Status: 201 Created          Time: 28 ms          Size: 189 B                                      |
| Response Body:                                                                                     |
| {                                                                                                  |
|   "id": 15,                                                                                        |
|   "customer_name": "Michael Scott",                                                                |
|   "item": "Chicken Fettuccine Alfredo",                                                            |
|   "quantity": 3,                                                                                   |
|   "status": "pending",                                                                             |
|   "created_at": "2026-10-18T21:20:50.560Z"                                                         |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
```

---

### Demonstration B: Validation Failure Request (HTTP 400 Bad Request)
- **Endpoint:** `POST http://127.0.0.1:8000/api/orders/place/`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "customer_name": "Michael Scott",
    "item": "Chicken Fettuccine Alfredo",
    "quantity": -2
  }
  ```

#### Postman Screenshot Simulation:
```
+----------------------------------------------------------------------------------------------------+
| POST  http://127.0.0.1:8000/api/orders/place/                                   [Send]             |
+----------------------------------------------------------------------------------------------------+
| Headers: Content-Type: application/json                                                            |
| Body (raw JSON):                                                                                   |
| {                                                                                                  |
|   "customer_name": "Michael Scott",                                                                |
|   "item": "Chicken Fettuccine Alfredo",                                                            |
|   "quantity": -2                                                                                   |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
| Status: 400 Bad Request      Time: 16 ms          Size: 112 B                                      |
| Response Body:                                                                                     |
| {                                                                                                  |
|   "quantity": [                                                                                    |
|     "Quantity must be a positive integer greater than zero."                                       |
|   ]                                                                                                |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
```

---

## Step 2: Test & Debug (Without AI)

### Bugs & Critical Limitations Identified in AI Solution:
1. **Bypassed DRF Serializer Layer:** The AI parsed `request.data.get()` manually and constructed the response dictionary by hand, completely bypassing DRF’s `ModelSerializer`, schema generation, and automatic data sanitization.
2. **Missing Validation on `customer_name` and `item`:** The code allowed blank strings (`""`), pure whitespace (`"   "`), or malicious payload injections for both customer name and dish item.
3. **Boolean Trap in Python:** In Python, `isinstance(True, int)` evaluates to `True` (since `bool` subclasses `int`), so passing `{"quantity": true}` would be accepted as an order of quantity 1!
4. **Lack of Transaction Atomicity:** Bypassing `transaction.atomic()` risks inconsistent database states under concurrent loads or failure hooks.

---

### Corrected Code (Production-Ready)

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.db import transaction
from .models import Order


class OrderPlaceSerializer(serializers.ModelSerializer):
    """
    Dedicated ModelSerializer enforcing field types, sanitization,
    and business rule validations.
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
            raise serializers.ValidationError("Customer name must be at least 2 characters long.")
        return cleaned

    def validate_item(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Item name cannot be empty.")
        return cleaned

    def validate_quantity(self, value):
        # Prevent booleans from slipping through (in Python, True is an instance of int)
        if isinstance(value, bool) or not isinstance(value, int):
            raise serializers.ValidationError("Quantity must be a valid integer.")
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer greater than zero.")
        return value


class PlaceOrderAPIView(APIView):
    """
    Refactored, production-ready order placement view.
    """
    def post(self, request):
        serializer = OrderPlaceSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = request.user if request.user and request.user.is_authenticated else None
                saved_order = serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

---

## Submission — All 3 Items Required

### 1. Exact AI Prompt(s)
> *"Act as a Senior Django REST Framework developer. I need an API endpoint in Django REST Framework to place food orders: 1. Implement a POST /api/orders/place/ endpoint using DRF APIView that accepts customer_name, item, and quantity in the request body. 2. Validate that quantity is a positive integer and return a JSON error response with HTTP 400 Bad Request if validation fails. 3. Save the order to the database using an Order model and return the saved order details (including the auto-generated id) with HTTP 201 Created on success. 4. Show me the complete view and URL pattern."*

---

### 2. Original and Corrected Code
*(See the full code blocks provided above in Step 1 and Step 2, and in `original_ai_code.py` & `corrected_code.py`).*

---

### 3. Explanation of Changes (3–4 Line Note)
> **Explanation of Changes:**  
> The AI's original version bypassed DRF's serializer architecture, manually parsing raw dictionary keys without sanitizing customer name or item strings, and allowed Python booleans (`True`) to pass as valid integer quantities. I replaced manual request parsing with a dedicated `OrderPlaceSerializer` that validates string cleanliness, prevents non-integer/boolean type exploitation, and standardizes validation errors to DRF's contract. Additionally, database creation was wrapped inside `transaction.atomic()` with optional user association to guarantee database consistency and security in production.
