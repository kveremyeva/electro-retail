from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from store.views import ProviderViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'providers', ProviderViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
