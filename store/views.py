from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Provider, Product
from .serializers import ProviderSerializer, ProductSerializer
from .permissions import IsActiveEmployee
from .filters import ProviderFilter


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [IsActiveEmployee]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProviderFilter


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsActiveEmployee]
