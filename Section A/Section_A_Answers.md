# Section A — Concept Application

**Program:** Python  
**Assessment Code:** M5-A1  
**Module:** Django REST Framework (DRF) & REST API Architecture  

---

## Question 1: REST Statelessness

### Scenario
You are building a multi-city food delivery API that will be consumed by both a mobile app and a web frontend. The frontend team asks why the API must be stateless.

### Question
Explain what statelessness means in the context of REST and describe how this principle affects the way your food delivery API handles user session data between requests.

---

### Answer & Analysis

#### 1. Definition of Statelessness in REST
In REST (Representational State Transfer) architecture, **statelessness** is a core architectural constraint (defined by Roy Fielding). It mandates that **each request from a client to a server must contain all the information necessary to understand and process that request**. The server must not store any client context or conversational state on server memory or server-side session stores across requests.

Every single HTTP request is processed independently and in complete isolation:
- The server does not remember that "Request B" comes from the same user who just issued "Request A".
- There is no server-side HTTP session affinity (sticky sessions) tying a client to a specific server instance.

```
Client (Web / Mobile)                  API Gateway / Load Balancer              Server Nodes
        |                                          |                           [Node 1]  [Node 2]  [Node 3]
        |--- Request 1: POST /api/orders/ -------->|------------------------------>|
        |    Header: Authorization: Token xyz123   | (Node 1 validates token, saves order, forgets state)
        |                                          |
        |--- Request 2: GET /api/my-orders/ ------>|----------------------------------------->|
             Header: Authorization: Token xyz123   | (Node 3 independently validates token, queries DB)
```

#### 2. Impact on the Multi-City Food Delivery API

In a multi-city food delivery application (which experiences high concurrency, rapid traffic surges during lunch/dinner, and unpredictable mobile connectivity), statelessness directly dictates how authentication and session data are handled:

1. **Self-Contained Client Credentials (Token-Based Authentication):**
   - Instead of storing a session cookie mapped to a server-side session table or in-memory dictionary (`request.session['user_id']`), the client stores an authentication token (e.g., DRF Token or JWT) locally in `AsyncStorage` (mobile) or `localStorage`/`HttpOnly Cookie` (web).
   - Every request to the delivery API includes the token in the HTTP header:
     ```http
     Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
     ```
   - Any server instance behind a load balancer can authenticate the user on the fly by validating the token against the central database or verifying the cryptographic signature (JWT).

2. **Session / Cart State Maintained by the Client:**
   - In traditional stateful web apps, the "active cart" might live in server session memory.
   - In our stateless REST API, the client manages cart items locally (or syncs explicit cart records in a database table via explicit IDs). Each request to create or update an order contains the full payload: restaurant ID, delivery address, item IDs, and quantities.
   - If a customer switches from 5G to Wi-Fi, or if the mobile app process gets killed in the background, no server-side connection state is lost.

3. **Horizontal Scalability Across Multiple Cities:**
   - Statelessness allows the infrastructure to scale horizontally across multiple instances (e.g., AWS ECS, Kubernetes pods, or GCP Cloud Run).
   - A request from Delhi can hit `Server Node 1`, and the very next request from the same user can hit `Server Node 4` without requiring session synchronization or distributed session replication (like sticky sessions or shared session caches).

4. **Reliability and Fault Tolerance:**
   - If a backend worker crashes midway through a peak lunch rush, no active user sessions are destroyed. The load balancer simply retries the stateless request on another healthy worker node.

---

## Question 2: Serializer vs. ModelSerializer

### Scenario
You are developing a restaurant management endpoint where a mobile app submits new menu items via a POST request. Your team is debating whether to use a plain `Serializer` or a `ModelSerializer`.

### Question
Justify why `ModelSerializer` is the better choice for this use case, and describe at least two specific field-level validations you would add to protect the data integrity of menu items.

---

### Answer & Analysis

#### 1. Justification for `ModelSerializer`
For the restaurant management endpoint where mobile apps submit new menu items to be persisted into a database, **`ModelSerializer` is significantly superior to a plain `serializers.Serializer`** for the following reasons:

| Feature | Plain `Serializer` | `ModelSerializer` (Preferred) |
| :--- | :--- | :--- |
| **Field Duplication** | Must manually re-declare every field (`CharField`, `DecimalField`, `ForeignKey`) already defined on the Django model. | Automatically inspects the `MenuItem` model and generates matching serializer fields, types, and flags. |
| **Validation Reuse** | Default model validators (e.g., `max_length`, `unique`, `blank`, `null`) must be hand-coded again. | Automatically imports and enforces all model-level constraints, validators, and relationships. |
| **CRUD Implementations** | Developer must manually write boilerplate `create(validated_data)` and `update(instance, validated_data)` methods. | Comes with battle-tested default implementations of `.create()` and `.update()`, directly returning saved model instances. |
| **Foreign Key Handling**| Relational mapping (e.g., `category_id` lookup) requires manual query logic or explicit relation fields. | Natively handles relational fields (`PrimaryKeyRelatedField`, Slug, or nested relations) with automatic queryset resolution. |
| **Maintainability** | Adding a column to the model requires updating both `models.py` and `serializers.py` manually (DRY violation). | Follows DRY (Don't Repeat Yourself) principle. Adding or updating model fields immediately reflects in the serializer. |

**Conclusion:** Menu items directly map to a database model (`MenuItem`). Using `ModelSerializer` saves substantial boilerplate, prevents synchronization errors between the model and serializer, and leverages DRF's automatic `.create()` method.

#### 2. Specific Field-Level Validations for Menu Items

To protect data integrity, the following two field-level validators must be implemented using DRF's `validate_<field_name>` convention:

##### Validation 1: Price Must Be Strictly Greater Than Zero
A menu item cannot be free ($0.00) or have a negative price due to accidental input, client glitches, or malicious tampering.

```python
from rest_framework import serializers
from .models import MenuItem
from decimal import Decimal

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'category', 'is_available']

    def validate_price(self, value):
        """
        Field-level validation: Ensures price is greater than 0.
        """
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Price must be greater than 0. Free or negative prices are not allowed.")
        if value > Decimal('9999.99'):
            raise serializers.ValidationError("Price exceeds maximum permitted threshold ($9999.99).")
        return value
```

##### Validation 2: Menu Item Name Cleanliness and Minimum Length
Menu item names should not consist only of whitespace, empty characters, or spam strings:

```python
    def validate_name(self, value):
        """
        Field-level validation: Ensures menu item name is trimmed and has meaningful length.
        """
        cleaned_name = value.strip()
        if len(cleaned_name) < 2:
            raise serializers.ValidationError("Menu item name must be at least 2 characters long and cannot be blank.")
        return cleaned_name
```

*Bonus Object-Level Validation:* You can also validate that duplicate items are not created under the same category by adding a multi-field validator:
```python
    def validate(self, attrs):
        name = attrs.get('name')
        category = attrs.get('category')
        if MenuItem.objects.filter(category=category, name__iexact=name).exists():
            raise serializers.ValidationError({"name": "A menu item with this name already exists in this category."})
        return attrs
```

---

## Question 3: ModelViewSet and DefaultRouter

### Scenario
You are organising the URL structure for a food ordering API that exposes three resources: Restaurants, Menus, and Orders. Currently, each resource has five individual APIView classes mapped to five separate URL patterns.

### Question
Explain how refactoring this to use a `ModelViewSet` with a `DefaultRouter` reduces URL management overhead, and identify which HTTP methods are automatically handled by `ModelViewSet`.

---

### Answer & Analysis

#### 1. How ModelViewSet + DefaultRouter Reduces URL Management Overhead

Currently, the project suffers from severe URL configuration bloat:
- **Before Refactoring:**
  - 3 resources $\times$ 5 `APIView` classes = **15 separate view classes**.
  - 3 resources $\times$ 5 URL patterns = **15 explicit `path(...)` entries** in `urls.py`.
  - For example, each resource required:
    1. `restaurants/` (GET -> list)
    2. `restaurants/create/` (POST -> create)
    3. `restaurants/<int:pk>/` (GET -> detail)
    4. `restaurants/<int:pk>/update/` (PUT/PATCH -> update)
    5. `restaurants/<int:pk>/delete/` (DELETE -> destroy)

- **After Refactoring (with `ModelViewSet` and `DefaultRouter`):**
  - **Single Class per Resource:** All 5 operations per resource are consolidated into a single `ModelViewSet` inheriting from `viewsets.ModelViewSet`.
  - **Zero Manual Regex/Path Patterns:** Instead of defining 15 paths, you register the viewsets with a single `DefaultRouter`:
    ```python
    from rest_framework.routers import DefaultRouter
    from .views import RestaurantViewSet, MenuViewSet, OrderViewSet

    router = DefaultRouter()
    router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
    router.register(r'menus', MenuViewSet, basename='menu')
    router.register(r'orders', OrderViewSet, basename='order')

    urlpatterns = [
        path('api/', include(router.urls)),
    ]
    ```
  - **Standardized RESTful Conventions:** Eliminates human error in URL naming, trailing slashes, and regex matching.
  - **Free API Root View & Format Suffixes:** `DefaultRouter` automatically generates a hyperlinked API root view (`/api/`) displaying all registered resources, as well as optional format suffix matching (e.g., `/api/orders.json`).

#### 2. HTTP Methods Automatically Handled by `ModelViewSet`

A `ModelViewSet` inherits from `GenericAPIView` and all 5 action mixins (`ListModelMixin`, `CreateModelMixin`, `RetrieveModelMixin`, `UpdateModelMixin`, `DestroyModelMixin`). The `DefaultRouter` maps the standard HTTP methods to specific action handlers as follows:

| URL Pattern | HTTP Method | ViewSet Action Method | Operation / Description |
| :--- | :--- | :--- | :--- |
| `/api/<resource>/` | **GET** | `list()` | List all instances of the resource |
| `/api/<resource>/` | **POST** | `create()` | Create a new instance |
| `/api/<resource>/{lookup}/` | **GET** | `retrieve()` | Retrieve a single instance by primary key |
| `/api/<resource>/{lookup}/` | **PUT** | `update()` | Completely replace/update a single instance |
| `/api/<resource>/{lookup}/` | **PATCH** | `partial_update()` | Partially update specific fields of an instance |
| `/api/<resource>/{lookup}/` | **DELETE** | `destroy()` | Remove/delete a single instance |
| `/api/<resource>/` | **OPTIONS** / **HEAD**| `metadata()` | Automatic HTTP metadata, schema, and headers |

---

## Question 4: Pagination and Performance

### Scenario
You are designing a dish search endpoint that returns all available dishes across 500+ restaurants. A QA engineer reports that responses take over 8 seconds on a standard connection.

### Question
Identify the most likely cause of this performance issue and justify which DRF pagination class you would choose to fix it. Compare the trade-offs between `PageNumberPagination` and `CursorPagination` for this scenario.

---

### Answer & Analysis

#### 1. Root Cause of the Performance Issue
The 8-second response latency is caused by **unpaginated database querying and full result set serialization**:
1. **Unbounded Database Retrieval:** Querying all dishes across 500+ restaurants retrieves tens of thousands (or hundreds of thousands) of rows into Django ORM memory at once (`SELECT * FROM dishes...`).
2. **Heavy Python Serialization Overhead:** Instantiating and executing `DishSerializer(many=True)` over 20,000+ objects consumes massive CPU time and memory to transform Django model instances into Python dictionaries and validate them.
3. **Huge JSON Payload Transfer:** A multi-megabyte JSON payload must be rendered into bytes and transferred over the network, causing severe bandwidth congestion and high client-side parsing time on mobile devices.

#### 2. Comparison & Trade-Offs: `PageNumberPagination` vs. `CursorPagination`

| Dimension | `PageNumberPagination` (`?page=2`) | `CursorPagination` (`?cursor=cD0yMDI2...`) |
| :--- | :--- | :--- |
| **SQL Mechanism** | Uses SQL `LIMIT` and `OFFSET` (e.g. `OFFSET 5000 LIMIT 20`). | Uses keyset pagination (e.g. `WHERE id > 1024 ORDER BY id ASC LIMIT 20`). |
| **Deep Paging Performance** | **Degrades drastically** at high offsets because the database engine must scan and discard thousands of rows. | **Constant $O(1)$ time complexity** regardless of how deep the user pages, since it seeks directly via the indexed ordering column. |
| **Data Consistency & Drift** | Vulnerable to page-shift anomalies: If new dishes are added or deleted while the user is paging, items can be duplicated or skipped. | **Completely immune to item skipping or duplicates** during live concurrent data insertions/deletions. |
| **Page Navigation Flexibility** | Allows jumping directly to arbitrary pages (e.g., jump straight to page 15). Shows total item count and total pages. | Only supports forward and backward navigation ("Next" / "Previous"). Does not show total page count. |
| **Ordering Requirement** | Can order by any field or multiple fields. | **Requires a strictly unique, immutable, ordered column** (typically `created_at` or `id`). |

#### 3. Justification of the Chosen Solution for Dish Search
**Recommended Choice: `CursorPagination`** (or a hybridized strategy)
- **Why `CursorPagination` is ideal:**
  - A food discovery app is typically consumed via mobile feeds with **infinite scrolling**. Users scroll continuously down the feed of dishes.
  - In a live multi-restaurant delivery system, restaurants frequently toggle dish availability, add seasonal specials, or update statuses in real-time. With `PageNumberPagination`, a customer scrolling through dishes would experience annoying skips or duplicate dishes as new items are added.
  - `CursorPagination` ensures ultra-fast, index-seek queries without expensive `COUNT(*)` database calculations on massive tables, immediately dropping response times from 8 seconds to under **50 milliseconds**.

*(Note: If the frontend explicitly requires numbered pagination controls [1, 2, 3...], `PageNumberPagination` with a fixed `page_size = 20` and optimized `select_related`/`prefetch_related` is used instead).*

---

## Question 5: Object-Level Permissions

### Scenario
You are debugging a food delivery API where a logged-in customer can view another customer's order history simply by changing the order ID in the URL. The `IsAuthenticated` permission is already applied.

### Question
Identify the specific gap in the current permission setup and explain how you would implement object-level permission to ensure each customer can only access their own orders.

---

### Answer & Analysis

#### 1. Identification of the Security Gap (IDOR Vulnerability)
The vulnerability is an **Insecure Direct Object Reference (IDOR)** (or BOLA — Broken Object Level Authorization, OWASP API Top 10 #1):
- `IsAuthenticated` only checks **global authentication** (i.e., "Is the incoming request from a valid logged-in user? Yes/No").
- It does **not check resource ownership or authorization** (i.e., "Does this specific order object belong to the user making the request?").
- Consequently, User A (logged in) passes `IsAuthenticated` and requests `GET /api/orders/45/`. The view fetches Order #45 without verifying if `order.customer == request.user`, leaking User B's order details, personal address, and payment information.

```
Attacker (User A) ---> GET /api/orders/45/ (belongs to User B)
                             |
                             V
                 [IsAuthenticated Check]  ==> PASSES (User A is a valid user)
                             |
                             V
                 [Object Ownership Check] ==> MISSING!
                             |
                             V
                   Returns User B's Order! (Security Breach)
```

#### 2. Implementation of Object-Level Permission in DRF

To completely solve this issue, we implement a custom DRF permission class using `BasePermission.has_object_permission()` and enforce ownership filtering:

##### Step 1: Create Custom Permission Class (`permissions.py`)
```python
from rest_framework import permissions

class IsOrderOwner(permissions.BasePermission):
    """
    Custom object-level permission to ensure users can only view or modify their own orders.
    Staff/Admins can be granted override access if desired.
    """
    def has_permission(self, request, view):
        # First ensure the user is authenticated
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Staff/superusers can view all orders for support
        if request.user.is_staff:
            return True
        # The order must belong to the logged-in customer
        return obj.customer == request.user
```

##### Step 2: Apply to the ViewSet / APIView (`views.py`)
```python
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer
from .permissions import IsOrderOwner

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsOrderOwner]

    def get_queryset(self):
        """
        Defense-in-Depth: Filter the queryset so list endpoints only return the user's orders.
        """
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user)
```

##### Step 3: Defense-in-Depth Guarantee
1. **At Queryset Level (`get_queryset`):** Filtering by `customer=request.user` ensures `/api/orders/` (list view) never reveals other people's orders.
2. **At Object Level (`check_object_permissions`):** If an attacker guesses an ID in `/api/orders/45/`, `has_object_permission` evaluates to `False`, returning an immediate **HTTP 403 Forbidden** (or HTTP 404 Not Found via `get_object()`).

---

## Question 6: Google Maps Geocoding API

### Scenario
You are optimising a restaurant discovery feature that currently stores only static latitude and longitude values in the database. A product manager requests a “find restaurants near me” option that accepts a user's address string.

### Question
Describe how you would integrate the Google Maps Geocoding API into a DRF view to convert an address string into coordinates and use those coordinates to return nearby restaurant results.

---

### Answer & Analysis

#### 1. Architecture Flow

```
[Client / Mobile App]
       |  GET /api/restaurants/nearby/?address=MG Road, Bengaluru&radius=5
       v
[DRF View: NearbyRestaurantAPIView]
       |
       |-- 1. Validate query parameter `address`
       |-- 2. Call Google Maps Geocoding API via HTTPS:
       |      https://maps.googleapis.com/maps/api/geocode/json?address=...&key=...
       |-- 3. Extract latitude & longitude from response JSON
       |-- 4. Calculate bounding box or Haversine distance over Restaurant model
       |-- 5. Serialize matching restaurants within radius (km)
       v
[Client receives filtered nearby restaurants with computed distances]
```

#### 2. Detailed Technical Implementation

##### Step 1: Environment Configuration
Store the Google Maps API Key securely in `.env` or Django `settings.py`:
```python
# settings.py
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyYourSecretKeyHere")
```

##### Step 2: Write the Geocoding Service Function
Create a modular service (`services/geocoding.py`) to keep views clean, handling timeouts, network errors, and caching:
```python
import requests
from django.conf import settings
from django.core.cache import cache

def geocode_address(address_string):
    """
    Converts an address string into (latitude, longitude) tuple using Google Geocoding API.
    Caches results in Redis/Django cache to save API quota.
    """
    cache_key = f"geocode:{address_string.strip().lower()}"
    cached_coords = cache.get(cache_key)
    if cached_coords:
        return cached_coords

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address_string,
        "key": settings.GOOGLE_MAPS_API_KEY
    }

    response = requests.get(url, params=params, timeout=5)
    if response.status_code != 200:
        return None

    data = response.json()
    if data.get("status") == "OK" and data.get("results"):
        location = data["results"][0]["geometry"]["location"]
        coords = (float(location["lat"]), float(location["lng"]))
        # Cache for 24 hours
        cache.set(cache_key, coords, timeout=86400)
        return coords
    return None
```

##### Step 3: Implement Haversine Distance in DRF View
To calculate geographic distance between the user's coordinates and restaurant database records without necessarily requiring PostGIS / GeoDjango:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import ACos, Cos, Radians, Sin
from .models import Restaurant
from .serializers import RestaurantSerializer
from .services.geocoding import geocode_address

class NearbyRestaurantAPIView(APIView):
    """
    Accepts an address string, geocodes it, and returns restaurants within a specified radius (km).
    Query Parameters:
      - address (required): e.g. "Connaught Place, New Delhi"
      - radius (optional, default 5 km)
    """
    def get(self, request):
        address = request.query_params.get('address')
        if not address:
            return Response(
                {"error": "The 'address' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        radius_km = float(request.query_params.get('radius', 5.0))

        # Step A: Convert Address to Coordinates
        coords = geocode_address(address)
        if not coords:
            return Response(
                {"error": "Could not geocode the provided address. Please enter a valid location."},
                status=status.HTTP_404_NOT_FOUND
            )

        user_lat, user_lng = coords

        # Step B: Haversine Formula via Django ORM Database Functions
        # Distance (km) = 6371 * acos(cos(radians(user_lat)) * cos(radians(lat)) *
        #                 cos(radians(lng) - radians(user_lng)) + sin(radians(user_lat)) * sin(radians(lat)))
        distance_expression = ExpressionWrapper(
            6371 * ACos(
                Cos(Radians(user_lat)) * Cos(Radians(F('latitude'))) *
                Cos(Radians(F('longitude')) - Radians(user_lng)) +
                Sin(Radians(user_lat)) * Sin(Radians(F('latitude')))
            ),
            output_field=FloatField()
        )

        nearby_restaurants = (
            Restaurant.objects.annotate(distance_km=distance_expression)
            .filter(distance_km__lte=radius_km)
            .order_by('distance_km')
        )

        serializer = RestaurantSerializer(nearby_restaurants, many=True)
        return Response({
            "user_location": {"latitude": user_lat, "longitude": user_lng, "formatted_address": address},
            "radius_km": radius_km,
            "total_found": nearby_restaurants.count(),
            "restaurants": serializer.data
        }, status=status.HTTP_200_OK)
```

##### Step 4: Key Production Considerations
- **API Quota & Cost Protection:** Cached in Redis so identical search queries don't incur redundant Google API billing.
- **Fail-safe Timeouts:** `timeout=5` prevents upstream third-party network hangs from locking server threads.
- **Bounding Box Optimization:** For millions of restaurant rows, filter first with a rough latitude/longitude bounding box index before applying Haversine math, or adopt PostGIS with DRF-GIS.
