from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from django.utils.safestring import mark_safe

from .models import (
    Product, Variation, CoffeeAttribute, TeaAttribute, AccessoryAttribute,
    TeaCategory, AccessoryType, CoffeeComposition, Aroma, Additive
)


# ============= INLINE КЛАССЫ ДЛЯ PRODUCTS =============

class VariationInline(admin.TabularInline):
    model = Variation
    extra = 1
    fields = ['price', 'weight', 'pieces', 'text_description_of_count', 'stock', 'available']
    readonly_fields = []


class CoffeeAttributeInline(admin.StackedInline):
    model = CoffeeAttribute
    extra = 0
    filter_horizontal = ['compositions', 'aromas', 'additives']
    fieldsets = (
        ('Основные характеристики', {
            'fields': ('coffee_type', 'roast', 'q_grading')
        }),
        ('Дополнительные характеристики', {
            'fields': ('compositions', 'aromas', 'additives'),
            'classes': ('collapse',)
        }),
    )


class TeaAttributeInline(admin.StackedInline):
    model = TeaAttribute
    extra = 0
    filter_horizontal = ['aromas', 'additives']
    fieldsets = (
        ('Основные характеристики', {
            'fields': ('tea_type', 'category')
        }),
        ('Дополнительные характеристики', {
            'fields': ('aromas', 'additives'),
            'classes': ('collapse',)
        }),
    )


class AccessoryAttributeInline(admin.StackedInline):
    model = AccessoryAttribute
    extra = 0
    fields = ['accessory_type', 'volume']


# ============= СПРАВОЧНИКИ =============

@admin.register(TeaCategory)
class TeaCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'products_count']
    search_fields = ['name']

    def products_count(self, obj):
        return obj.teaattribute_set.count()

    products_count.short_description = 'Количество товаров'


@admin.register(AccessoryType)
class AccessoryTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'products_count']
    search_fields = ['name']

    def products_count(self, obj):
        return obj.accessoryattribute_set.count()

    products_count.short_description = 'Количество товаров'


@admin.register(CoffeeComposition)
class CoffeeCompositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'usage_count']
    search_fields = ['name']

    def usage_count(self, obj):
        return obj.coffeeattribute_set.count()

    usage_count.short_description = 'Используется в'


@admin.register(Aroma)
class AromaAdmin(admin.ModelAdmin):
    list_display = ['name', 'used_in_coffee', 'used_in_tea', 'total_usage']
    search_fields = ['name']
    list_filter = ['coffeeattribute', 'teaattribute']

    def used_in_coffee(self, obj):
        return obj.coffeeattribute_set.count()

    used_in_coffee.short_description = 'В кофе'

    def used_in_tea(self, obj):
        return obj.teaattribute_set.count()

    used_in_tea.short_description = 'В чае'

    def total_usage(self, obj):
        return obj.coffeeattribute_set.count() + obj.teaattribute_set.count()

    total_usage.short_description = 'Всего использований'


@admin.register(Additive)
class AdditiveAdmin(admin.ModelAdmin):
    list_display = ['name', 'used_in_coffee', 'used_in_tea', 'total_usage']
    search_fields = ['name']
    list_filter = ['coffeeattribute', 'teaattribute']

    def used_in_coffee(self, obj):
        return obj.coffeeattribute_set.count()

    used_in_coffee.short_description = 'В кофе'

    def used_in_tea(self, obj):
        return obj.teaattribute_set.count()

    used_in_tea.short_description = 'В чае'

    def total_usage(self, obj):
        return obj.coffeeattribute_set.count() + obj.teaattribute_set.count()

    total_usage.short_description = 'Всего использований'


# ============= КАТАЛОГ =============

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'product_type', 'manufacturer', 'country',
        'variations_count', 'total_stock', 'available', 'has_attributes'
    ]
    list_filter = ['product_type', 'available', 'country', 'manufacturer']
    search_fields = ['name', 'manufacturer', 'description']
    list_editable = ['available']
    readonly_fields = ['variations_count', 'total_stock']
    list_per_page = 25

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'product_type', 'available')
        }),
        ('Производитель', {
            'fields': ('manufacturer', 'country', 'region')
        }),
        ('Статистика', {
            'fields': ('variations_count', 'total_stock'),
            'classes': ('collapse',)
        }),
    )

    inlines = [VariationInline]

    def get_inlines(self, request, obj):
        inlines = [VariationInline]
        if obj:
            if obj.product_type == 'coffee':
                inlines.append(CoffeeAttributeInline)
            elif obj.product_type == 'tea':
                inlines.append(TeaAttributeInline)
            elif obj.product_type == 'accessory':
                inlines.append(AccessoryAttributeInline)
        return inlines

    def variations_count(self, obj):
        return obj.variations.count()

    variations_count.short_description = 'Вариаций'

    def total_stock(self, obj):
        return sum(v.stock for v in obj.variations.all())

    total_stock.short_description = 'Общий остаток'

    def has_attributes(self, obj):
        attrs = []
        if hasattr(obj, 'coffee_attr'):
            attrs.append('☕')
        if hasattr(obj, 'tea_attr'):
            attrs.append('🍵')
        if hasattr(obj, 'accessory_attr'):
            attrs.append('🫖')
        return ''.join(attrs) if attrs else '❌'

    has_attributes.short_description = 'Атрибуты'


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = [
        'product_link', 'text_description_of_count', 'price',
        'stock', 'available', 'stock_status'
    ]
    list_filter = ['available', 'product__product_type']
    search_fields = ['product__name', 'text_description_of_count']
    list_editable = ['price', 'stock', 'available']
    list_select_related = ['product']
    list_per_page = 50

    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)

    product_link.short_description = 'Товар'

    def stock_status(self, obj):
        if obj.stock == 0:
            color = 'red'
            text = 'Нет в наличии'
        elif obj.stock < 10:
            color = 'orange'
            text = 'Мало'
        else:
            color = 'green'
            text = 'В наличии'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )

    stock_status.short_description = 'Статус склада'


# Атрибуты как отдельные админки для аналитики
@admin.register(CoffeeAttribute)
class CoffeeAttributeAdmin(admin.ModelAdmin):
    list_display = ['product', 'coffee_type', 'roast', 'q_grading']
    list_filter = ['coffee_type', 'roast']
    search_fields = ['product__name']
    filter_horizontal = ['compositions', 'aromas', 'additives']


@admin.register(TeaAttribute)
class TeaAttributeAdmin(admin.ModelAdmin):
    list_display = ['product', 'tea_type', 'category']
    list_filter = ['tea_type', 'category']
    search_fields = ['product__name']
    filter_horizontal = ['aromas', 'additives']


@admin.register(AccessoryAttribute)
class AccessoryAttributeAdmin(admin.ModelAdmin):
    list_display = ['product', 'accessory_type', 'volume']
    list_filter = ['accessory_type']
    search_fields = ['product__name']
