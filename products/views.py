from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product, BestSelling, Hot, Notification, Category, TrackingCode, ProductColor
from .serializers import (
    ProductSerializer, BestSellingSerializer, HotSerializer, NotificationSerializer,
    CategorySerializer, CategoryTreeSerializer, TrackingCodeSerializer
)

# Max products returned in one homepage payload (single request, no pagination)
HOMEPAGE_PRODUCTS_LIMIT = 100

# Prefetch active colors once so ProductSerializer.get_colors() uses cache (no N+1).
_active_colors_prefetch = Prefetch(
    'colors',
    queryset=ProductColor.objects.filter(is_active=True).order_by('order', 'name'),
)
_product_colors_prefetch = Prefetch(
    'product__colors',
    queryset=ProductColor.objects.filter(is_active=True).order_by('order', 'name'),
)


class HomepageView(APIView):
    """Single endpoint returning products, best_selling, and hot for the homepage.
    One request instead of three so the server handles one response and the page loads faster."""
    permission_classes = [AllowAny]

    def get(self, request):
        products_qs = (
            Product.objects.filter(is_active=True)
            .select_related('category', 'category__parent')
            .prefetch_related(_active_colors_prefetch)
            .order_by('-created_at')[:HOMEPAGE_PRODUCTS_LIMIT]
        )
        best_selling_qs = (
            BestSelling.objects.filter(is_active=True, product__is_active=True)
            .select_related('product', 'product__category', 'product__category__parent')
            .prefetch_related(_product_colors_prefetch)
            .order_by('order')
        )
        hot_qs = (
            Hot.objects.filter(is_active=True, product__is_active=True)
            .select_related('product', 'product__category', 'product__category__parent')
            .prefetch_related(_product_colors_prefetch)
            .order_by('order')
        )
        return Response({
            'products': ProductSerializer(products_qs, many=True).data,
            'best_selling': BestSellingSerializer(best_selling_qs, many=True).data,
            'hot': HotSerializer(hot_qs, many=True).data,
        })


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Category.objects.filter(is_active=True).select_related('parent')

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure (only parent categories with their children)"""
        parent_categories = Category.objects.filter(
            is_active=True,
            parent__isnull=True
        ).prefetch_related('children').order_by('order', 'name')
        serializer = CategoryTreeSerializer(parent_categories, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing products"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = (
            Product.objects.filter(is_active=True)
            .select_related('category', 'category__parent')
            .prefetch_related(_active_colors_prefetch)
        )
        # Optional: Add search/filter functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Category filtering by slug
        category = self.request.query_params.get('category', None)
        if category:
            # Filter by category slug - includes products in this category
            # or in child categories if this is a parent category
            try:
                cat = Category.objects.get(slug=category, is_active=True)
                if cat.parent is None:
                    # Parent category - get products from this category and all children
                    child_ids = cat.children.filter(is_active=True).values_list('id', flat=True)
                    queryset = queryset.filter(category_id__in=[cat.id] + list(child_ids))
                else:
                    # Child category - get products only from this category
                    queryset = queryset.filter(category=cat)
            except Category.DoesNotExist:
                queryset = queryset.none()
        
        return queryset


class BestSellingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing best selling products"""
    queryset = BestSelling.objects.filter(is_active=True, product__is_active=True)
    serializer_class = BestSellingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return BestSelling.objects.filter(
            is_active=True,
            product__is_active=True
        ).select_related('product', 'product__category', 'product__category__parent').prefetch_related(_product_colors_prefetch)


class HotViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing hot products (homepage Hot section)"""
    queryset = Hot.objects.filter(is_active=True, product__is_active=True)
    serializer_class = HotSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Hot.objects.filter(
            is_active=True,
            product__is_active=True
        ).select_related('product', 'product__category', 'product__category__parent').prefetch_related(_product_colors_prefetch)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the currently active notification"""
        notification = Notification.objects.filter(is_active=True).first()
        if notification:
            serializer = self.get_serializer(notification)
            return Response(serializer.data)
        return Response({'message': '', 'is_active': False})


class TrackingCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing tracking codes"""
    queryset = TrackingCode.objects.filter(is_active=True)
    serializer_class = TrackingCodeSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active tracking codes"""
        tracking_codes = TrackingCode.objects.filter(is_active=True)
        serializer = self.get_serializer(tracking_codes, many=True)
        return Response(serializer.data)
