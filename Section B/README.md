# Section B — Practical Coding Tasks

**Program:** Python · **Assessment Code:** M5-A1  
**Module:** Django REST Framework (DRF) Practical Implementation  

This directory contains complete, fully tested, and verified solutions for all 4 tasks under Section B.

---

## Directory Structure

```
Section B/
├── README.md                                          <- Main Section B documentation
├── section_b_project/                                 <- Complete, fully runnable Django project
│   ├── manage.py
│   ├── test_section_b.py                              <- Automated verification test suite (100% PASS)
│   ├── db.sqlite3                                     <- SQLite database with migrations applied
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py                                <- Configured TokenAuth & PageNumberPagination
│   │   ├── urls.py                                    <- Main routing including api.urls
│   │   └── wsgi.py
│   └── api/
│       ├── models.py                                  <- Category, MenuItem, Order models
│       ├── serializers.py                             <- Category, MenuItem, Order, PlaceOrder serializers
│       ├── views.py                                   <- Implements Tasks 1, 2, 3, 4 endpoints
│       ├── urls.py                                    <- Router + explicit paths
│       ├── admin.py
│       └── migrations/
├── Task 1 - Food Category Listing API/
│   └── README.md                                      <- Task 1 isolated code, endpoints & responses
├── Task 2 - Menu Item CRUD API/
│   └── README.md                                      <- Task 2 isolated code, endpoints & responses
├── Task 3 - Order Listing with ViewSets Router and Pagination/
│   └── README.md                                      <- Task 3 isolated code, endpoints & responses
└── Task 4 - Token-Authenticated Order Placement/
    └── README.md                                      <- Task 4 isolated code, endpoints & responses
```

---

## Task Summary Table

| Task | Title | Key Concepts Demonstrated | Endpoint(s) | HTTP Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| **Task 1** | Food Category Listing API | `ModelSerializer`, `ListAPIView`, migrations | `GET /api/categories/` | `200 OK` |
| **Task 2** | Menu Item CRUD API | `APIView`, `ModelSerializer`, field validation (`price > 0`) | `GET, POST /api/menu-items/`<br>`GET, PUT, DELETE /api/menu-items/<id>/` | `200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, `204 No Content` |
| **Task 3** | Order Listing with ViewSets, Router, and Pagination | `ModelViewSet`, `DefaultRouter`, `PageNumberPagination` (`PAGE_SIZE = 5`), `get_queryset()` status filtering | `GET, POST /api/orders/`<br>`GET, PUT, PATCH, DELETE /api/orders/<id>/`<br>`GET /api/orders/?status=pending` | `200 OK`, `201 Created` |
| **Task 4** | Token-Authenticated Order Placement | `TokenAuthentication`, `IsAuthenticated`, `request.user` ownership isolation | `POST /api/my-orders/`<br>`GET /api/my-orders/` | `201 Created`, `200 OK`, `401 Unauthorized` |

---

## How to Run & Verify Section B

### 1. Run Automated Test Suite
From the `Section B/section_b_project` directory, run:
```powershell
python test_section_b.py
```

**Output:**
```text
============================================================
RUNNING AUTOMATED VERIFICATION SUITE FOR SECTION B
============================================================
[AUTH] Alice Token: 425fe6988d35cf3f7fcab5657682273f34ffbadb
[AUTH] Bob Token:   842af1177ad3243d7b5b050a71c363c5da7200dc

--- Testing Task 1: Food Category Listing API ---
  [PASS] GET /api/categories/ returned HTTP 200 with 3 items.

--- Testing Task 2: Menu Item CRUD API ---
  [PASS] POST /api/menu-items/ (valid) -> HTTP 201 Created (ID: 1)
  [PASS] POST /api/menu-items/ (price <= 0) -> HTTP 400 Bad Request
  [PASS] GET /api/menu-items/1/ -> HTTP 200 OK
  [PASS] GET /api/menu-items/9999/ -> HTTP 404 Not Found
  [PASS] PUT /api/menu-items/1/ -> HTTP 200 OK (Updated name to XL)
  [PASS] DELETE /api/menu-items/1/ -> HTTP 204 No Content

--- Testing Task 3: Order Listing with ViewSets, Router, and Pagination ---
  [PASS] GET /api/orders/ paginated: total=12, page_size=5, next=http://testserver/api/orders/?page=2
  [PASS] GET /api/orders/?status=pending returned 6 filtered orders.

--- Testing Task 4: Token-Authenticated Order Placement ---
  [PASS] Unauthenticated POST /api/my-orders/ -> HTTP 401
  [PASS] Unauthenticated GET /api/my-orders/ -> HTTP 401
  [PASS] Authenticated Alice POST /api/my-orders/ -> HTTP 201 Created (Order #13)
  [PASS] Authenticated Alice GET /api/my-orders/ returned 1 order owned by Alice.
  [PASS] Authenticated Bob GET /api/my-orders/ returned 0 orders (Isolated ownership).

============================================================
ALL SECTION B TASKS (1, 2, 3, 4) PASSED 100% SUCCESSFULLY!
============================================================
```

### 2. Run the Development Server
```powershell
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/api/` in your browser or Postman.
