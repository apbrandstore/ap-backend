from django.contrib import admin
from .models import Product, BestSelling, Hot, Notification, Category, ProductColor, TrackingCode, SiteSettings


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    fields = ['name', 'image', 'order', 'is_active']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'order', 'is_active', 'created_at']
    list_filter = ['parent', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'slug', 'parent', 'order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            # Only show parent categories (those without a parent) as options
            kwargs["queryset"] = Category.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'regular_price', 'offer_price', 'stock', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'stock']
    inlines = [ProductColorInline]
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Product Images', {
            'fields': ('image', 'image2', 'image3', 'image4'),
            'description': 'Upload up to 4 product images. The first image is the main/primary image.'
        }),
        ('Pricing', {
            'fields': ('regular_price', 'offer_price'),
            'description': 'Set regular_price (required). Set offer_price (optional) to show a discounted price.'
        }),
        ('Inventory', {
            'fields': ('stock', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BestSelling)
class BestSellingAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__name', 'product__description']
    list_editable = ['order', 'is_active']
    fieldsets = (
        ('Best Selling Configuration', {
            'fields': ('product', 'order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Hot)
class HotAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__name', 'product__description']
    list_editable = ['order', 'is_active']
    fieldsets = (
        ('Hot Section', {
            'fields': ('product', 'order', 'is_active'),
            'description': 'Choose which products appear in the Hot section under the hero. Add up to 4 (or more) and set order. Lower order = first.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['message', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['message']
    list_editable = ['is_active']
    fieldsets = (
        ('Notification Message', {
            'fields': ('message', 'is_active'),
            'description': 'Only one notification can be active at a time. Activating a notification will deactivate others.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TrackingCode)
class TrackingCodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    list_editable = ['is_active']
    fieldsets = (
        ('Tracking Code Information', {
            'fields': ('name', 'code', 'is_active'),
            'description': 'Paste your tracking code here (e.g., Facebook Pixel base code). The code will be injected into the frontend automatically.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'hero_image', 'updated_at']
    fieldsets = (
        ('Homepage Hero', {
            'fields': ('hero_image',),
            'description': 'Upload a hero image to show on the homepage. Leave blank to use the default image.'
        }),
        ('Timestamps', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['updated_at']

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
