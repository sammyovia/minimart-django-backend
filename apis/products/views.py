# products/views.py

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated # Import these if not already
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .permissions import IsAdminOrReadOnly # Import your custom permission

class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer
    # Apply the permission class here
    permission_classes = [IsAdminOrReadOnly] # GET (list) is allowed for any, POST (create) only for staff/admin

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Apply the permission class here
    permission_classes = [IsAdminOrReadOnly] # GET (retrieve) is allowed for any, PUT/PATCH/DELETE only for staff/admin

# You would also create similar views for Category if needed:
class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]