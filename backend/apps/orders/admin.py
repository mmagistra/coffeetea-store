from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Order, OrderItem
from .forms import OrderItemForm


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemForm
    extra = 0
    readonly_fields = ['total_price', 'price']
    fields = ['product', 'variation', 'price', 'quantity', 'total_price']

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['total_price']
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('variation__product')
        return qs

    def total_price(self, obj):
        if obj.pk:
            return obj.price * obj.quantity
        return 0

    total_price.short_description = 'Сумма'

    class Media:
        js = ('admin/js/order_item_inline.js',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'full_name', 'status', 'paid',
        'total_items', 'total_amount', 'created'
    ]
    list_filter = ['status', 'paid', 'created', 'updated']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'user__username']
    list_editable = ['status', 'paid']
    readonly_fields = ['created', 'updated', 'total_items', 'total_amount']
    date_hierarchy = 'created'
    list_per_page = 25



    fieldsets = (
        ('Информация о заказе', {
            'fields': ('user', 'status', 'paid', 'created', 'updated')
        }),
        ('Контактная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Статистика', {
            'fields': ('total_items', 'total_amount'),
            'classes': ('collapse',)
        }),
    )

    inlines = [OrderItemInline]

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = 'Полное имя'

    def total_items(self, obj):
        return obj.items.count()

    total_items.short_description = 'Позиций'

    def total_amount(self, obj):
        return sum(item.price * item.quantity for item in obj.items.all())

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related(
            'items__variation__product',
            'items__variation',
        )
        return qs

    total_amount.short_description = 'Сумма заказа ₽'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'variation', 'price', 'quantity', 'total_price']
    list_filter = ['order__created', 'variation__product__product_type']
    search_fields = ['order__first_name', 'order__last_name', 'variation__product__name']
    readonly_fields = ['price', 'total_price']
    list_select_related = ['order', 'variation__product']

    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">Заказ #{}</a>', url, obj.order.pk)

    order_link.short_description = 'Заказ'

    def total_price(self, obj):
        return obj.price * obj.quantity

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('order', 'variation__product')
        return qs

    total_price.short_description = 'Сумма ₽'
