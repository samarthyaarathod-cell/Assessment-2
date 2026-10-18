from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    MenuItemViewSet,
    OrderViewSet,
    RegisterUserView,
    CustomAuthTokenView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'menu-items', MenuItemViewSet, basename='menuitem')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterUserView.as_view(), name='api-auth-register'),
    path('auth/login/', CustomAuthTokenView.as_view(), name='api-auth-login'),

    # DefaultRouter CRUD endpoints for Category, MenuItem, and Order
    path('', include(router.urls)),
]
