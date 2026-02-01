from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HomepageView,
    ProductViewSet,
    BestSellingViewSet,
    HotViewSet,
    NotificationViewSet,
    CategoryViewSet,
    TrackingCodeViewSet,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'best-selling', BestSellingViewSet, basename='best-selling')
router.register(r'hot', HotViewSet, basename='hot')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'tracking-codes', TrackingCodeViewSet, basename='tracking-code')

urlpatterns = [
    path('api/homepage/', HomepageView.as_view(), name='homepage'),
    path('api/', include(router.urls)),
]

