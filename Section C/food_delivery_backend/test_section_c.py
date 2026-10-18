import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_delivery.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from api.models import Category, MenuItem, Order

def run_tests():
    print("=" * 65)
    print("RUNNING AUTOMATED CAPSTONE VERIFICATION FOR SECTION C")
    print("=" * 65)

    client = APIClient()

    # 1. Setup Test Users
    user, _ = User.objects.get_or_create(username='john_doe', email='john@example.com')
    user.set_password('securepass123')
    user.save()
    token, _ = Token.objects.get_or_create(user=user)

    admin_user, _ = User.objects.get_or_create(username='admin_boss', email='admin@example.com', is_staff=True)
    admin_user.set_password('adminpass123')
    admin_user.save()
    admin_token, _ = Token.objects.get_or_create(user=admin_user)

    print(f"[AUTH] User Token:  {token.key}")
    print(f"[AUTH] Admin Token: {admin_token.key}")

    # ========================================================
    # Requirement 1 & 2: Category CRUD & Validation
    # ========================================================
    print("\n--- Testing Category Resource CRUD & Validation ---")
    Category.objects.all().delete()

    # Validation: Empty name should fail with 400
    res_bad_cat = client.post('/api/categories/', {"name": "  ", "description": "Empty"}, format='json')
    assert res_bad_cat.status_code == 400, f"Expected 400 for empty name, got {res_bad_cat.status_code}"
    print("  [PASS] Empty category name rejected with HTTP 400.")

    # Create Category
    res_cat1 = client.post('/api/categories/', {"name": "Italian Cuisine", "description": "Handmade pasta and pizza"}, format='json')
    assert res_cat1.status_code == 201, f"Expected 201, got {res_cat1.status_code}"
    cat1_id = res_cat1.data['id']
    print(f"  [PASS] Created Category #{cat1_id}: Italian Cuisine (HTTP 201)")

    res_cat2 = client.post('/api/categories/', {"name": "Burgers & Grills", "description": "Gourmet burgers and sides"}, format='json')
    assert res_cat2.status_code == 201
    cat2_id = res_cat2.data['id']

    # Retrieve & Update
    res_get_cat = client.get(f'/api/categories/{cat1_id}/')
    assert res_get_cat.status_code == 200

    res_put_cat = client.put(f'/api/categories/{cat1_id}/', {"name": "Classic Italian", "description": "Authentic regional Italian"}, format='json')
    assert res_put_cat.status_code == 200
    assert res_put_cat.data['name'] == "Classic Italian"
    print("  [PASS] Category Retrieve and Update succeeded (HTTP 200).")

    # ========================================================
    # Requirement 1 & 2: MenuItem CRUD & Validation (Price > 0, Name Non-Empty)
    # ========================================================
    print("\n--- Testing MenuItem Resource CRUD & Validation ---")
    MenuItem.objects.all().delete()

    # Validation: Price <= 0 should fail with 400
    res_bad_price = client.post('/api/menu-items/', {
        "name": "Zero Price Pizza",
        "price": "0.00",
        "category": cat1_id,
        "is_available": True
    }, format='json')
    assert res_bad_price.status_code == 400
    assert "Price must be strictly greater than 0" in str(res_bad_price.data)
    print("  [PASS] Price <= 0 rejected with HTTP 400.")

    # Create valid menu items
    res_item1 = client.post('/api/menu-items/', {
        "name": "Wood-Fired Margherita",
        "price": "14.50",
        "category": cat1_id,
        "is_available": True
    }, format='json')
    assert res_item1.status_code == 201
    item1_id = res_item1.data['id']
    print(f"  [PASS] Created MenuItem #{item1_id}: Wood-Fired Margherita (HTTP 201)")

    res_item2 = client.post('/api/menu-items/', {
        "name": "Truffle Bacon Burger",
        "price": "16.75",
        "category": cat2_id,
        "is_available": True
    }, format='json')
    assert res_item2.status_code == 201

    # List & Retrieve
    res_items_list = client.get('/api/menu-items/')
    assert res_items_list.status_code == 200
    assert len(res_items_list.data) == 2
    print("  [PASS] MenuItems listed successfully (HTTP 200).")

    # ========================================================
    # Requirement 3: Order Authentication & 401 Protection
    # ========================================================
    print("\n--- Testing Order Authentication & HTTP 401 Protection ---")
    Order.objects.all().delete()

    # Unauthenticated Order List -> 401
    res_unauth_list = client.get('/api/orders/')
    assert res_unauth_list.status_code == 401, f"Expected 401, got {res_unauth_list.status_code}"
    print(f"  [PASS] Unauthenticated GET /api/orders/ rejected with HTTP 401: {res_unauth_list.data}")

    # Unauthenticated Order Create -> 401
    res_unauth_create = client.post('/api/orders/', {"item": "Pizza", "quantity": 1}, format='json')
    assert res_unauth_create.status_code == 401
    print(f"  [PASS] Unauthenticated POST /api/orders/ rejected with HTTP 401.")

    # ========================================================
    # Requirement 2 & 3: Authenticated Order Creation & Quantity Validation
    # ========================================================
    print("\n--- Testing Authenticated Order Creation & Validation ---")
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # Validation: Quantity < 1 should fail with 400
    res_bad_qty = client.post('/api/orders/', {"item": "Pizza", "quantity": 0}, format='json')
    assert res_bad_qty.status_code == 400
    assert "Quantity must be greater than or equal to 1" in str(res_bad_qty.data)
    print("  [PASS] Quantity < 1 rejected with HTTP 400.")

    # Valid Order Creation
    for i in range(1, 14):
        status_val = 'pending' if i % 2 == 1 else 'delivered'
        res_ord = client.post('/api/orders/', {
            "item": f"Delicious Special #{i}",
            "quantity": i,
            "status": status_val
        }, format='json')
        assert res_ord.status_code == 201

    print("  [PASS] Seeded 13 authenticated orders for John Doe.")

    # ========================================================
    # Requirement 4: Order Pagination (page_size = 5) & Status Filtering
    # ========================================================
    print("\n--- Testing Order Pagination & Status Query Filtering ---")

    # Pagination: page_size = 5
    res_page1 = client.get('/api/orders/')
    assert res_page1.status_code == 200
    assert res_page1.data['count'] == 13
    assert len(res_page1.data['results']) == 5
    assert res_page1.data['next'] is not None
    print(f"  [PASS] GET /api/orders/ paginated (Total: {res_page1.data['count']}, Page Size: {len(res_page1.data['results'])})")

    # Status filter: ?status=pending
    res_pending = client.get('/api/orders/?status=pending')
    assert res_pending.status_code == 200
    assert res_pending.data['count'] == 7, f"Expected 7 pending orders, got {res_pending.data['count']}"
    for item in res_pending.data['results']:
        assert item['status'] == 'pending'
    print(f"  [PASS] GET /api/orders/?status=pending correctly returned {res_pending.data['count']} pending orders.")

    # Status filter: ?status=delivered
    res_delivered = client.get('/api/orders/?status=delivered')
    assert res_delivered.status_code == 200
    assert res_delivered.data['count'] == 6
    print(f"  [PASS] GET /api/orders/?status=delivered correctly returned {res_delivered.data['count']} delivered orders.")

    print("\n" + "=" * 65)
    print("ALL SECTION C CAPSTONE REQUIREMENTS VERIFIED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == '__main__':
    run_tests()
