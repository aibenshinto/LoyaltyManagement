from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Product, User
from .serializers import ProductSerializer, UserSerializer

# Register user
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# Add product (Admin only)
class AddProductView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

# List all products (Authenticated users)
class ListProductsView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]