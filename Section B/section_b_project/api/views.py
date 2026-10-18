from rest_framework import generics, viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .models import Category, MenuItem, Order
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    OrderSerializer,
    PlaceOrderSerializer
)


# ==========================================
# TASK 1: Food Category Listing API
# ==========================================
class CategoryListAPIView(generics.ListAPIView):
    """
    Task 1: Read-only DRF ListAPIView endpoint mapped to /api/categories/
    Returns all food categories as a JSON array with HTTP 200.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None  # Ensure raw unpaginated JSON array per Task 1 spec


# ==========================================
# TASK 2: Menu Item CRUD API (APIView)
# ==========================================
class MenuItemListCreateAPIView(APIView):
    """
    Task 2:
    - List: GET /api/menu-items/ (HTTP 200)
    - Create: POST /api/menu-items/ (HTTP 201 on success, HTTP 400 on validation failure)
    """
    def get(self, request):
        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuItemDetailAPIView(APIView):
    """
    Task 2:
    - Retrieve: GET /api/menu-items/<id>/ (HTTP 200, or HTTP 404 if not found)
    - Update: PUT /api/menu-items/<id>/ (HTTP 200 on success, HTTP 400 on invalid, HTTP 404 if not found)
    - Delete: DELETE /api/menu-items/<id>/ (HTTP 204 on success, HTTP 404 if not found)
    """
    def get_object(self, pk):
        try:
            return MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            return None

    def get(self, request, pk):
        item = self.get_object(pk)
        if item is None:
            return Response(
                {"error": f"MenuItem with id {pk} was not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = MenuItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        item = self.get_object(pk)
        if item is None:
            return Response(
                {"error": f"MenuItem with id {pk} was not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = MenuItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = self.get_object(pk)
        if item is None:
            return Response(
                {"error": f"MenuItem with id {pk} was not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        item.delete()
        return Response(
            {"message": f"MenuItem {pk} successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )


# ==========================================
# TASK 3: Order Listing with ViewSets & Pagination
# ==========================================
class OrderPagination(PageNumberPagination):
    """
    Task 3: PageNumberPagination with PAGE_SIZE = 5.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class OrderViewSet(viewsets.ModelViewSet):
    """
    Task 3: ModelViewSet registered with DefaultRouter.
    Auto-generates CRUD URLs under /api/orders/.
    Applies PageNumberPagination (PAGE_SIZE = 5).
    Filters orders by status query parameter using get_queryset().
    """
    serializer_class = OrderSerializer
    pagination_class = OrderPagination

    def get_queryset(self):
        queryset = Order.objects.all().order_by('-id')
        status_param = self.request.query_params.get('status', None)
        if status_param is not None:
            queryset = queryset.filter(status__iexact=status_param.strip())
        return queryset


# ==========================================
# TASK 4: Token-Authenticated Order Placement
# ==========================================
class MyOrdersAPIView(APIView):
    """
    Task 4:
    Protected endpoint using TokenAuthentication and IsAuthenticated permission.
    - POST /api/my-orders/ : Place an order and save request.user as order owner.
    - GET /api/my-orders/ : Return only the orders belonging to the authenticated user.
    - Unauthenticated requests receive HTTP 401 with a meaningful message.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def handle_exception(self, exc):
        """
        Ensures a meaningful HTTP 401 error message when authentication fails or is missing.
        """
        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            return Response(
                {
                    "error": "Unauthorized",
                    "detail": "Authentication credentials were not provided or token is invalid. Please provide a valid Authorization: Token <key> header."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().handle_exception(exc)

    def get(self, request):
        user_orders = Order.objects.filter(user=request.user).order_by('-id')
        serializer = OrderSerializer(user_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        if serializer.is_valid():
            # Save request.user as the order owner
            customer_name = serializer.validated_data.get('customer_name')
            if not customer_name:
                customer_name = request.user.get_full_name() or request.user.username

            saved_order = serializer.save(
                user=request.user,
                customer_name=customer_name
            )
            response_serializer = OrderSerializer(saved_order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# Token Generation Helper for Testers
# ==========================================
class ObtainAuthTokenView(APIView):
    """
    Helper endpoint to obtain or generate token for test users:
    POST /api/auth/token/ with {"username": "...", "password": "..."}
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
                return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.pk,
            "username": user.username
        }, status=status.HTTP_200_OK)
