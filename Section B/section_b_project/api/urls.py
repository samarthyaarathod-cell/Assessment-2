from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryListAPIView,
    MenuItemListCreateAPIView,
    MenuItemDetailAPIView,
    OrderViewSet,
    MyOrdersAPIView,
    ObtainAuthTokenView
)

# DefaultRouter for Task 3
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # Task 1: Food Category Listing API
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),

    # Task 2: Menu Item CRUD API (APIView)
    path('menu-items/', MenuItemListCreateAPIView.as_view(), name='menuitem-list-create'),
    path('menu-items/<int:pk>/', MenuItemDetailAPIView.as_view(), name='menuitem-detail'),

    # Task 4: Token-Authenticated Order Placement & Customer Order History
    path('my-orders/', MyOrdersAPIView.as_view(), name='my-orders'),

    # Helper: Obtain token for test users
    path('auth/token/', ObtainAuthTokenView.as_view(), name='api-token-auth'),

    # Task 3: Order Listing with ViewSets & Router (auto-generates /api/orders/)
    path('', include(router.urls)),
]
