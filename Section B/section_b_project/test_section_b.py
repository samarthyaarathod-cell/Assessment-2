import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from api.models import Category, MenuItem, Order
from decimal import Decimal

def run_tests():
    print("=" * 60)
    print("RUNNING AUTOMATED VERIFICATION SUITE FOR SECTION B")
    print("=" * 60)

    client = APIClient()

    # 0. Setup test users and tokens
    user_alice, _ = User.objects.get_or_create(username='alice', email='alice@example.com')
    user_alice.set_password('password123')
    user_alice.save()
    token_alice, _ = Token.objects.get_or_create(user=user_alice)

    user_bob, _ = User.objects.get_or_create(username='bob', email='bob@example.com')
    user_bob.set_password('password123')
    user_bob.save()
    token_bob, _ = Token.objects.get_or_create(user=user_bob)

    print(f"[AUTH] Alice Token: {token_alice.key}")
    print(f"[AUTH] Bob Token:   {token_bob.key}")

    # ==========================================
    # Task 1: Food Category Listing API
    # ==========================================
    print("\n--- Testing Task 1: Food Category Listing API ---")
    Category.objects.all().delete()
    cat_pizza = Category.objects.create(name="Pizza", description="Artisan wood-fired pizzas")
    cat_burgers = Category.objects.create(name="Burgers", description="Juicy gourmet burgers and fries")
    cat_desserts = Category.objects.create(name="Desserts", description="Cakes, ice creams, and sweet delights")

    res = client.get('/api/categories/')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert isinstance(res.data, list), "Expected JSON array response"
    assert len(res.data) == 3, f"Expected 3 categories, got {len(res.data)}"
    print(f"  [PASS] GET /api/categories/ returned HTTP 200 with {len(res.data)} items.")

    # ==========================================
    # Task 2: Menu Item CRUD API
    # ==========================================
    print("\n--- Testing Task 2: Menu Item CRUD API ---")
    MenuItem.objects.all().delete()

    # 2.1: Create valid item (POST -> 201)
    payload_valid = {
        "name": "Margherita Supreme",
        "price": "14.99",
        "category": cat_pizza.id,
        "is_available": True
    }
    res_create = client.post('/api/menu-items/', payload_valid, format='json')
    assert res_create.status_code == 201, f"Expected 201, got {res_create.status_code}: {res_create.data}"
    item_id = res_create.data['id']
    print(f"  [PASS] POST /api/menu-items/ (valid) -> HTTP 201 Created (ID: {item_id})")

    # 2.2: Create invalid item with price <= 0 (POST -> 400)
    payload_invalid = {
        "name": "Free Pizza Error",
        "price": "-5.00",
        "category": cat_pizza.id,
        "is_available": True
    }
    res_invalid = client.post('/api/menu-items/', payload_invalid, format='json')
    assert res_invalid.status_code == 400, f"Expected 400, got {res_invalid.status_code}"
    print(f"  [PASS] POST /api/menu-items/ (price <= 0) -> HTTP 400 Bad Request: {res_invalid.data}")

    # 2.3: Retrieve item (GET /id/ -> 200)
    res_get = client.get(f'/api/menu-items/{item_id}/')
    assert res_get.status_code == 200, f"Expected 200, got {res_get.status_code}"
    assert res_get.data['name'] == "Margherita Supreme"
    print(f"  [PASS] GET /api/menu-items/{item_id}/ -> HTTP 200 OK")

    # 2.4: Retrieve non-existent item (GET /id/ -> 404)
    res_get_404 = client.get('/api/menu-items/9999/')
    assert res_get_404.status_code == 404, f"Expected 404, got {res_get_404.status_code}"
    print(f"  [PASS] GET /api/menu-items/9999/ -> HTTP 404 Not Found: {res_get_404.data}")

    # 2.5: Update item (PUT /id/ -> 200)
    payload_update = {
        "name": "Margherita Supreme XL",
        "price": "17.99",
        "category": cat_pizza.id,
        "is_available": True
    }
    res_put = client.put(f'/api/menu-items/{item_id}/', payload_update, format='json')
    assert res_put.status_code == 200, f"Expected 200, got {res_put.status_code}"
    assert res_put.data['name'] == "Margherita Supreme XL"
    print(f"  [PASS] PUT /api/menu-items/{item_id}/ -> HTTP 200 OK (Updated name to XL)")

    # 2.6: Delete item (DELETE /id/ -> 204)
    res_del = client.delete(f'/api/menu-items/{item_id}/')
    assert res_del.status_code == 204, f"Expected 204, got {res_del.status_code}"
    print(f"  [PASS] DELETE /api/menu-items/{item_id}/ -> HTTP 204 No Content")

    # ==========================================
    # Task 3: Order Listing with ViewSets, Router, and Pagination
    # ==========================================
    print("\n--- Testing Task 3: Order Listing with ViewSets, Router, and Pagination ---")
    Order.objects.all().delete()
    for i in range(1, 13):
        status_choice = 'pending' if i % 2 == 1 else 'delivered'
        Order.objects.create(
            customer_name=f"Customer {i}",
            item=f"Item #{i}",
            quantity=i,
            status=status_choice
        )

    # 3.1: Verify router-generated listing and pagination PAGE_SIZE = 5
    res_orders = client.get('/api/orders/')
    assert res_orders.status_code == 200, f"Expected 200, got {res_orders.status_code}"
    assert 'count' in res_orders.data, "Expected paginated response containing 'count'"
    assert res_orders.data['count'] == 12, f"Expected 12 total orders, got {res_orders.data['count']}"
    assert len(res_orders.data['results']) == 5, f"Expected page size of 5, got {len(res_orders.data['results'])}"
    print(f"  [PASS] GET /api/orders/ paginated: total={res_orders.data['count']}, page_size={len(res_orders.data['results'])}, next={res_orders.data['next']}")

    # 3.2: Verify status filter: /api/orders/?status=pending
    res_filtered = client.get('/api/orders/?status=pending')
    assert res_filtered.status_code == 200
    assert res_filtered.data['count'] == 6, f"Expected 6 pending orders, got {res_filtered.data['count']}"
    for ord_item in res_filtered.data['results']:
        assert ord_item['status'] == 'pending', f"Expected status pending, got {ord_item['status']}"
    print(f"  [PASS] GET /api/orders/?status=pending returned {res_filtered.data['count']} filtered orders.")

    # ==========================================
    # Task 4: Token-Authenticated Order Placement
    # ==========================================
    print("\n--- Testing Task 4: Token-Authenticated Order Placement ---")

    # 4.1: Unauthenticated request should return 401 with meaningful message
    res_unauth_post = client.post('/api/my-orders/', {"item": "Pasta Alfredo", "quantity": 2}, format='json')
    assert res_unauth_post.status_code == 401, f"Expected 401, got {res_unauth_post.status_code}"
    assert "Unauthorized" in str(res_unauth_post.data) or "detail" in str(res_unauth_post.data)
    print(f"  [PASS] Unauthenticated POST /api/my-orders/ -> HTTP 401: {res_unauth_post.data}")

    res_unauth_get = client.get('/api/my-orders/')
    assert res_unauth_get.status_code == 401, f"Expected 401, got {res_unauth_get.status_code}"
    print(f"  [PASS] Unauthenticated GET /api/my-orders/ -> HTTP 401: {res_unauth_get.data}")

    # 4.2: Authenticated request by Alice (POST -> 201)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_alice.key}')
    alice_order_payload = {
        "item": "Truffle Pasta",
        "quantity": 2
    }
    res_alice_order = client.post('/api/my-orders/', alice_order_payload, format='json')
    assert res_alice_order.status_code == 201, f"Expected 201, got {res_alice_order.status_code}"
    assert res_alice_order.data['customer_name'] == 'alice'
    print(f"  [PASS] Authenticated Alice POST /api/my-orders/ -> HTTP 201 Created (Order #{res_alice_order.data['id']})")

    # 4.3: Authenticated GET /api/my-orders/ by Alice should return only Alice's orders
    res_alice_history = client.get('/api/my-orders/')
    assert res_alice_history.status_code == 200
    assert len(res_alice_history.data) == 1
    assert res_alice_history.data[0]['item'] == 'Truffle Pasta'
    print(f"  [PASS] Authenticated Alice GET /api/my-orders/ returned 1 order owned by Alice.")

    # 4.4: Authenticated GET /api/my-orders/ by Bob should return 0 orders
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_bob.key}')
    res_bob_history = client.get('/api/my-orders/')
    assert res_bob_history.status_code == 200
    assert len(res_bob_history.data) == 0
    print(f"  [PASS] Authenticated Bob GET /api/my-orders/ returned 0 orders (Isolated ownership).")

    print("\n" + "=" * 60)
    print("ALL SECTION B TASKS (1, 2, 3, 4) PASSED 100% SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
