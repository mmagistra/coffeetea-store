from django.contrib import admin
from django.urls.base import reverse
from django.utils.html import format_html

from .models import Cart, CartItem, Wishlist, WishlistItem
from .forms import CartItemForm, CartForm, WishlistForm


class CartItemInline(admin.TabularInline):
    model = CartItem
    form = CartItemForm
    extra = 0
    fields = ['product', 'variation', 'quantity', 'added_at']
    readonly_fields = ['added_at']
    # autocomplete_fields = ['product']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('variation__product')
        return qs

    class Media:
        js = ('admin/js/cart_item_inline.js',)


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    fields = ['product', 'added_at']
    readonly_fields = ['added_at']
    autocomplete_fields = ['product']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    form = CartForm
    list_display = ['id', 'owner_info', 'items_count', 'created', 'updated']
    list_filter = ['created', 'updated']
    search_fields = ['user__username', 'owner_info']
    readonly_fields = ['created', 'updated', 'items_count']
    autocomplete_fields = ['user']
    list_per_page = 25

    inlines = [CartItemInline]

    def owner_info(self, obj):
        if obj.user:
            return f"👤 {obj.user.username}"
        else:
            return f"🔑 {obj.session_key[:10]}..."

    owner_info.short_description = 'user / session'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('items', 'user')
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = 'products in cart'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['owner_info', 'variation_info', 'quantity', 'added_at']
    list_filter = ['added_at', 'variation__product__product_type']
    search_fields = ['cart__user__username', 'variation__product__name', 'variation__text_description_of_count']
    date_hierarchy = 'added_at'
    list_select_related = ['cart__user', 'variation__product']
    list_per_page = 25

    def variation_info(self, obj):
        return f"{obj.variation.product.name} | {obj.variation.text_description_of_count}"

    def owner_info(self, obj):
        url = reverse('admin:customer_collections_cart_change', args=[obj.cart.pk])
        if obj.cart.user:
            return format_html('<a href="{}">👤 {}</a>', url, obj.cart.user.username)
        else:
            return format_html('<a href="{}">🔑 {}</a>', url, obj.cart.session_key[:8])

    owner_info.short_description = 'user / session'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    form = WishlistForm
    list_display = ['owner_info', 'items_count', 'created', 'updated']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created', 'updated', 'items_count']
    autocomplete_fields = ['user']
    list_select_related = ['user']
    list_per_page = 25

    inlines = [WishlistItemInline]

    def items_count(self, obj):
        return obj.items.count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('items')
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def owner_info(self, obj):
        if obj.user:
            return f"👤 {obj.user.username}"
        else:
            return f"🔑 {obj.session_key[:10]}..."

    owner_info.short_description = 'user / session'
    items_count.short_description = 'products in wishlist'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['owner_info_link', 'product', 'added_at']
    list_filter = ['added_at', 'product__product_type']
    search_fields = ['wishlist__user__username', 'product__name']
    date_hierarchy = 'added_at'
    list_select_related = ['wishlist__user', 'product']
    list_per_page = 25

    def owner_info_link(self, obj):
        url = reverse('admin:customer_collections_wishlist_change', args=[obj.wishlist.pk])
        if obj.wishlist.user:
            return format_html('<a href="{}">👤 {}</a>', url, obj.wishlist.user.username)
        else:
            return format_html('<a href="{}">🔑 {}</a>', url, obj.wishlist.session_key[:8])

    def wishlist_user(self, obj):
        return obj.wishlist.user.username

    owner_info_link.short_description = 'user / session'
