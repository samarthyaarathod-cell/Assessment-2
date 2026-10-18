from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from django.contrib.auth.models import User

from .models import Category, MenuItem, Order
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    OrderSerializer
)


class CustomPagination(PageNumberPagination):
    """
    Standard pagination class with PAGE_SIZE = 5 as required by specification.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD ModelViewSet for Category resource.
    Registered with DefaultRouter.
    Endpoints:
      - GET /api/categories/ (list)
      - POST /api/categories/ (create)
      - GET /api/categories/<id>/ (retrieve)
      - PUT /api/categories/<id>/ (update)
      - PATCH /api/categories/<id>/ (partial_update)
      - DELETE /api/categories/<id>/ (destroy)
    """
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    pagination_class = None  # Categories return full list


class MenuItemViewSet(viewsets.ModelViewSet):
    """
    CRUD ModelViewSet for MenuItem resource.
    Registered with DefaultRouter.
    Endpoints:
      - GET /api/menu-items/ (list)
      - POST /api/menu-items/ (create)
      - GET /api/menu-items/<id>/ (retrieve)
      - PUT /api/menu-items/<id>/ (update)
      - PATCH /api/menu-items/<id>/ (partial_update)
      - DELETE /api/menu-items/<id>/ (destroy)
    """
    queryset = MenuItem.objects.select_related('category').all().order_by('id')
    serializer_class = MenuItemSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD ModelViewSet for Order resource.
    - Protected with TokenAuthentication and IsAuthenticated.
    - Unauthenticated requests receive HTTP 401 with a meaningful message.
    - Paginated with PageNumberPagination (page_size = 5).
    - Supports status query filtering: /api/orders/?status=pending
    - Automatic customer isolation: only returns the current user's orders.
    """
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def handle_exception(self, exc):
        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            return Response(
                {
                    "error": "Unauthorized",
                    "status_code": 401,
                    "detail": "Authentication credentials were not provided or token is invalid. Provide header: 'Authorization: Token <key>'."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().handle_exception(exc)

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Order.objects.none()

        # Admin/staff can see all orders; regular customers only see their own orders
        if user.is_staff:
            queryset = Order.objects.all().order_by('-id')
        else:
            queryset = Order.objects.filter(user=user).order_by('-id')

        # Filter by status query param (e.g., ?status=pending)
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status__iexact=status_param.strip())

        return queryset

    def perform_create(self, serializer):
        customer_name = serializer.validated_data.get('customer_name')
        if not customer_name:
            customer_name = self.request.user.get_full_name() or self.request.user.username

        serializer.save(
            user=self.request.user,
            customer_name=customer_name
        )


# ==========================================
# Authentication & User Management Views
# ==========================================
class RegisterUserView(APIView):
    """
    User registration endpoint:
    POST /api/auth/register/ with {"username": "...", "password": "...", "email": "..."}
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        if not username or not password:
            return Response(
                {"error": "Both username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "A user with this username already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(username=username, password=password, email=email)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "User registered successfully.",
            "user_id": user.pk,
            "username": user.username,
            "token": token.key
        }, status=status.HTTP_201_CREATED)


class CustomAuthTokenView(APIView):
    """
    Obtain Auth Token endpoint:
    POST /api/auth/login/ with {"username": "...", "password": "..."}
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "Both username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                return Response(
                    {"error": "Invalid password credentials."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except User.DoesNotExist:
            return Response(
                {"error": "User with this username does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.pk,
            "username": user.username
        }, status=status.HTTP_200_OK)
