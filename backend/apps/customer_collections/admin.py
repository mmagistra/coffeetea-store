from django.contrib import admin

from .models import Cart, CartItem, Wishlist, WishlistItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['variation', 'quantity', 'added_at']
    readonly_fields = ['added_at']


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    fields = ['product', 'added_at']
    readonly_fields = ['added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_info', 'items_count', 'created', 'updated']
    list_filter = ['created', 'updated']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created', 'updated', 'items_count']

    inlines = [CartItemInline]

    def session_info(self, obj):
        if obj.user:
            return f"👤 {obj.user.username}"
        else:
            return f"🔑 {obj.session_key[:10]}..."

    session_info.short_description = 'Пользователь/Сессия'

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = 'Товаров'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart_info', 'variation', 'quantity', 'added_at']
    list_filter = ['added_at', 'variation__product__product_type']
    search_fields = ['cart__user__username', 'variation__product__name']
    date_hierarchy = 'added_at'
    list_select_related = ['cart__user', 'variation__product']

    def cart_info(self, obj):
        if obj.cart.user:
            return f"Корзина: {obj.cart.user.username}"
        else:
            return f"Анонимная корзина: {obj.cart.session_key[:8]}..."

    cart_info.short_description = 'Корзина'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'items_count', 'created', 'updated']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created', 'updated', 'items_count']

    inlines = [WishlistItemInline]

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = 'Товаров в избранном'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['wishlist_user', 'product', 'added_at']
    list_filter = ['added_at', 'product__product_type']
    search_fields = ['wishlist__user__username', 'product__name']
    date_hierarchy = 'added_at'
    list_select_related = ['wishlist__user', 'product']

    def wishlist_user(self, obj):
        return obj.wishlist.user.username

    wishlist_user.short_description = 'Пользователь'
