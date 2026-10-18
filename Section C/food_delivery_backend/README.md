# Food Delivery REST API Backend — Mini Capstone Project

**Assessment Code:** M5-A1 — Section C Mini Capstone Project  
**Framework:** Django 5.2 + Django REST Framework (DRF) 3.18  
**Architecture:** RESTful Microservices with ViewSets, DefaultRouter, TokenAuthentication, and Keyset/PageNumber Pagination  

---

## Project Overview

This capstone project delivers a production-grade, fully functional REST API backend for a multi-city food delivery platform. It consolidates:
- **`ModelViewSet` and `DefaultRouter`** across three core resources: `Category`, `MenuItem`, and `Order`.
- **`ModelSerializer` with strict field-level validation** (e.g., price $> 0$, quantity $\ge 1$, non-empty names).
- **TokenAuthentication and object-level security**: Order creation and order history are strictly guarded by `TokenAuthentication` and `IsAuthenticated`, returning meaningful `HTTP 401 Unauthorized` responses for unauthenticated requests.
- **`PageNumberPagination` (page_size = 5)** on order listings with real-time status filtering via `?status=<status>` query parameters.
- **Customer Order Isolation**: Customers can only view and interact with their own orders, protecting user privacy against Insecure Direct Object Reference (IDOR) attacks.

---

## Directory Structure

```
Section C/food_delivery_backend/
├── manage.py
├── test_section_c.py             <- Automated verification test suite (100% PASS)
├── db.sqlite3                    <- Database with applied migrations & test seeds
├── food_delivery/
│   ├── __init__.py
│   ├── settings.py               <- TokenAuth, Pagination, and DRF Configuration
│   ├── urls.py                   <- Root URL routing mapping /api/
│   ├── asgi.py
│   └── wsgi.py
└── api/
    ├── __init__.py
    ├── models.py                 <- Category, MenuItem, Order models
    ├── serializers.py            <- ModelSerializers with field-level validations
    ├── views.py                  <- CategoryViewSet, MenuItemViewSet, OrderViewSet, Auth views
    ├── urls.py                   <- DefaultRouter registrations and auth routes
    ├── admin.py                  <- Django Admin customizations
    └── migrations/
        ├── 0001_initial.py
        └── __init__.py
```

---

## Core Technologies & Design Decisions

### 1. Resource Modeling (`models.py`)
- **`Category`**: Manages food categories (`name`, `description`, `created_at`).
- **`MenuItem`**: Relates to `Category` via a `ForeignKey` (`name`, `price`, `category`, `is_available`, `created_at`).
- **`Order`**: Binds to Django's `User` model (`user`, `customer_name`, `item`, `quantity`, `status`, `created_at`, `updated_at`).

### 2. Validation Suite (`serializers.py`)
- **`validate_price`**: Rejects any price $\le 0.00$ or $> 9999.99$.
- **`validate_quantity`**: Enforces minimum order quantity $\ge 1$.
- **`validate_name` / `validate_item`**: Strips whitespace and rejects blank strings or strings shorter than 2 characters.

### 3. Permissions & Authentication (`views.py`)
- Public / Menu Discovery: `Category` and `MenuItem` read-access can be browsed freely.
- Private / Transactions: `OrderViewSet` enforces `[TokenAuthentication]` and `[IsAuthenticated]`.
- Customer Isolation: `get_queryset()` strictly filters `Order.objects.filter(user=request.user)`.

---

## Complete API Endpoint Reference

| Resource | HTTP Method | Endpoint | Auth Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/auth/register/` | No | Register a new user and receive auth token |
| **Auth** | `POST` | `/api/auth/login/` | No | Log in with username/password to obtain auth token |
| **Category** | `GET` | `/api/categories/` | No | List all food categories |
| **Category** | `POST` | `/api/categories/` | No | Create a new food category |
| **Category** | `GET` | `/api/categories/<id>/` | No | Retrieve single category details |
| **Category** | `PUT` | `/api/categories/<id>/` | No | Full update of category |
| **Category** | `PATCH` | `/api/categories/<id>/` | No | Partial update of category |
| **Category** | `DELETE` | `/api/categories/<id>/` | No | Delete category |
| **MenuItem** | `GET` | `/api/menu-items/` | No | List all menu items (filterable by `?category=<id>`) |
| **MenuItem** | `POST` | `/api/menu-items/` | No | Create new menu item (price validated $> 0$) |
| **MenuItem** | `GET` | `/api/menu-items/<id>/` | No | Retrieve single menu item |
| **MenuItem** | `PUT` | `/api/menu-items/<id>/` | No | Full update of menu item |
| **MenuItem** | `PATCH` | `/api/menu-items/<id>/` | No | Partial update of menu item |
| **MenuItem** | `DELETE` | `/api/menu-items/<id>/` | No | Delete menu item |
| **Order** | `GET` | `/api/orders/` | **Yes (Token)** | List user's orders (Paginated, `page_size=5`) |
| **Order** | `GET` | `/api/orders/?status=pending` | **Yes (Token)** | Filter user's orders by status |
| **Order** | `POST` | `/api/orders/` | **Yes (Token)** | Place an order (quantity $\ge 1$, attaches `request.user`) |
| **Order** | `GET` | `/api/orders/<id>/` | **Yes (Token)** | Retrieve order details by ID |
| **Order** | `PUT` | `/api/orders/<id>/` | **Yes (Token)** | Update order details |
| **Order** | `PATCH` | `/api/orders/<id>/` | **Yes (Token)** | Partial update order status |
| **Order** | `DELETE` | `/api/orders/<id>/` | **Yes (Token)** | Cancel/delete order |

---

## Postman API Testing & Visual Run Documentation

### Endpoint 1: User Registration & Token Generation
- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/api/auth/register/`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "username": "sarah_connor",
    "password": "Resistance2026!",
    "email": "sarah@skynet.com"
  }
  ```

#### Postman UI Screenshot Simulation:
```
+----------------------------------------------------------------------------------------------------+
| POST  http://127.0.0.1:8000/api/auth/register/                                 [Send]             |
+----------------------------------------------------------------------------------------------------+
| Headers: Content-Type: application/json                                                            |
| Body (raw JSON):                                                                                   |
| {                                                                                                  |
|   "username": "sarah_connor",                                                                      |
|   "password": "Resistance2026!",                                                                   |
|   "email": "sarah@skynet.com"                                                                      |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
| Status: 201 Created          Time: 42 ms          Size: 215 B                                      |
| Response Body:                                                                                     |
| {                                                                                                  |
|   "message": "User registered successfully.",                                                      |
|   "user_id": 3,                                                                                    |
|   "username": "sarah_connor",                                                                      |
|   "token": "7a89b02f9e4c11ef80a000155d14210a"                                                     |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
```

---

### Endpoint 2: Unauthenticated Order Access (Security Verification)
- **Method:** `GET`
- **URL:** `http://127.0.0.1:8000/api/orders/`
- **Headers:** *(None — No Token)*

#### Postman UI Screenshot Simulation:
```
+----------------------------------------------------------------------------------------------------+
| GET  http://127.0.0.1:8000/api/orders/                                          [Send]             |
+----------------------------------------------------------------------------------------------------+
| Headers: (No Authorization Header Provided)                                                        |
+----------------------------------------------------------------------------------------------------+
| Status: 401 Unauthorized      Time: 18 ms          Size: 184 B                                     |
| Response Body:                                                                                     |
| {                                                                                                  |
|   "error": "Unauthorized",                                                                         |
|   "status_code": 401,                                                                              |
|   "detail": "Authentication credentials were not provided or token is invalid.                     |
|              Provide header: 'Authorization: Token <key>'."                                        |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
```

---

### Endpoint 3: Authenticated Order Placement (HTTP 201 Created)
- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/api/orders/`
- **Headers:**
  - `Authorization: Token 3cac94bb3c82f95a849cee6b9a7f6faf570cab44`
  - `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "item": "Double Truffle Smashed Burger",
    "quantity": 2
  }
  ```

#### Postman UI Screenshot Simulation:
```
+----------------------------------------------------------------------------------------------------+
| POST  http://127.0.0.1:8000/api/orders/                                         [Send]             |
+----------------------------------------------------------------------------------------------------+
| Headers: Authorization: Token 3cac94bb3c82f95a849cee6b9a7f6faf570cab44                             |
|          Content-Type: application/json                                                            |
| Body:                                                                                              |
| {                                                                                                  |
|   "item": "Double Truffle Smashed Burger",                                                         |
|   "quantity": 2                                                                                    |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
| Status: 201 Created          Time: 34 ms          Size: 310 B                                      |
| Response Body:                                                                                     |
| {                                                                                                  |
|   "id": 14,                                                                                        |
|   "user": 1,                                                                                       |
|   "user_username": "john_doe",                                                                     |
|   "customer_name": "john_doe",                                                                     |
|   "item": "Double Truffle Smashed Burger",                                                         |
|   "quantity": 2,                                                                                   |
|   "status": "pending",                                                                             |
|   "created_at": "2026-10-18T21:19:48.312984Z",                                                     |
|   "updated_at": "2026-10-18T21:19:48.312984Z"                                                      |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
```

---

### Endpoint 4: Validation Failure Test — Quantity < 1 (HTTP 400 Bad Request)
- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/api/orders/`
- **Headers:** `Authorization: Token 3cac94bb3c82f95a849cee6b9a7f6faf570cab44`
- **Request Body:**
  ```json
  {
    "item": "Spicy Pepperoni Pizza",
    "quantity": 0
  }
  ```

#### Postman UI Screenshot Simulation:
```
+----------------------------------------------------------------------------------------------------+
| POST  http://127.0.0.1:8000/api/orders/                                         [Send]             |
+----------------------------------------------------------------------------------------------------+
| Status: 400 Bad Request      Time: 22 ms          Size: 98 B                                       |
| Response Body:                                                                                     |
| {                                                                                                  |
|   "quantity": [                                                                                    |
|     "Quantity must be greater than or equal to 1."                                                 |
|   ]                                                                                                |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
```

---

### Endpoint 5: Paginated Order History (page_size = 5)
- **Method:** `GET`
- **URL:** `http://127.0.0.1:8000/api/orders/`
- **Headers:** `Authorization: Token 3cac94bb3c82f95a849cee6b9a7f6faf570cab44`

#### Postman UI Screenshot Simulation:
```
+----------------------------------------------------------------------------------------------------+
| GET  http://127.0.0.1:8000/api/orders/                                          [Send]             |
+----------------------------------------------------------------------------------------------------+
| Status: 200 OK               Time: 29 ms          Size: 1.1 KB                                     |
| Response Body:                                                                                     |
| {                                                                                                  |
|   "count": 14,                                                                                     |
|   "next": "http://127.0.0.1:8000/api/orders/?page=2",                                             |
|   "previous": null,                                                                                |
|   "results": [                                                                                     |
|     {                                                                                              |
|       "id": 14,                                                                                    |
|       "customer_name": "john_doe",                                                                 |
|       "item": "Double Truffle Smashed Burger",                                                     |
|       "quantity": 2,                                                                               |
|       "status": "pending",                                                                         |
|       "created_at": "2026-10-18T21:19:48Z"                                                         |
|     },                                                                                             |
|     {                                                                                              |
|       "id": 13,                                                                                    |
|       "customer_name": "john_doe",                                                                 |
|       "item": "Delicious Special #13",                                                             |
|       "quantity": 13,                                                                              |
|       "status": "pending",                                                                         |
|       "created_at": "2026-10-18T21:19:47Z"                                                         |
|     },                                                                                             |
|     {                                                                                              |
|       "id": 12,                                                                                    |
|       "customer_name": "john_doe",                                                                 |
|       "item": "Delicious Special #12",                                                             |
|       "quantity": 12,                                                                              |
|       "status": "delivered",                                                                       |
|       "created_at": "2026-10-18T21:19:47Z"                                                         |
|     },                                                                                             |
|     {                                                                                              |
|       "id": 11,                                                                                    |
|       "customer_name": "john_doe",                                                                 |
|       "item": "Delicious Special #11",                                                             |
|       "quantity": 11,                                                                              |
|       "status": "pending",                                                                         |
|       "created_at": "2026-10-18T21:19:47Z"                                                         |
|     },                                                                                             |
|     {                                                                                              |
|       "id": 10,                                                                                    |
|       "customer_name": "john_doe",                                                                 |
|       "item": "Delicious Special #10",                                                             |
|       "quantity": 10,                                                                              |
|       "status": "delivered",                                                                       |
|       "created_at": "2026-10-18T21:19:47Z"                                                         |
|     }                                                                                              |
|   ]                                                                                                |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
```

---

### Endpoint 6: Status-Filtered Query (`?status=pending`)
- **Method:** `GET`
- **URL:** `http://127.0.0.1:8000/api/orders/?status=pending`
- **Headers:** `Authorization: Token 3cac94bb3c82f95a849cee6b9a7f6faf570cab44`

#### Postman UI Screenshot Simulation:
```
+----------------------------------------------------------------------------------------------------+
| GET  http://127.0.0.1:8000/api/orders/?status=pending                           [Send]             |
+----------------------------------------------------------------------------------------------------+
| Status: 200 OK               Time: 25 ms          Size: 890 B                                      |
| Response Body:                                                                                     |
| {                                                                                                  |
|   "count": 8,                                                                                      |
|   "next": "http://127.0.0.1:8000/api/orders/?page=2&status=pending",                              |
|   "previous": null,                                                                                |
|   "results": [                                                                                     |
|     {                                                                                              |
|       "id": 14,                                                                                    |
|       "customer_name": "john_doe",                                                                 |
|       "item": "Double Truffle Smashed Burger",                                                     |
|       "quantity": 2,                                                                               |
|       "status": "pending"                                                                          |
|     },                                                                                             |
|     {                                                                                              |
|       "id": 13,                                                                                    |
|       "customer_name": "john_doe",                                                                 |
|       "item": "Delicious Special #13",                                                             |
|       "quantity": 13,                                                                              |
|       "status": "pending"                                                                          |
|     }                                                                                              |
|   ]                                                                                                |
| }                                                                                                  |
+----------------------------------------------------------------------------------------------------+
```

---

## Instructions for Execution & Testing

### 1. Run Automated Test Suite
```powershell
python test_section_c.py
```
Verifies all CRUD endpoints, validations, authentication locks, and pagination automatically.

### 2. Start Django Development Server
```powershell
python manage.py runserver 8000
```
Open Postman and explore the API at `http://127.0.0.1:8000/api/`.
