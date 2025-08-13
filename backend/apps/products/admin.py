from django.contrib import admin
from django.urls.conf import path
from django.utils.html import format_html
from django.urls import reverse
from rangefilter.filters import NumericRangeFilterBuilder

from .filters import AromaFilter, AdditiveFilter, ManufacturerFilter, CountryFilter, TeaCategoryFilter, StockFilter
from .forms import CoffeeAttributeForm, CoffeeAttributeInlineForm
from .models import (
    Product, Variation, CoffeeAttribute, TeaAttribute, AccessoryAttribute,
    TeaCategory, AccessoryType, Aroma, Additive, Country, Manufacturer
)


class VariationInline(admin.TabularInline):
    model = Variation
    extra = 1
    fields = ['price', 'weight', 'pieces', 'text_description_of_count', 'stock', 'available']
    readonly_fields = []


class CoffeeAttributeInline(admin.StackedInline):
    form = CoffeeAttributeInlineForm

    model = CoffeeAttribute
    extra = 0
    filter_horizontal = ['aromas', 'additives']
    fieldsets = (
        ('Основные характеристики', {
            'fields': ('coffee_type', 'roast', 'q_grading')
        }),
        ('Дополнительные характеристики', {
            'fields': ('aromas', 'additives', 'arabica_percent', 'robusta_percent', 'liberica_percent'),
            'classes': ('collapse',)
        }),
    )

    # def compositions_info(self, obj):
    #     return f'{obj.arabica_percent}% (А), {obj.robusta_percent}% (Р), {obj.liberica_percent}% (Л)'


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


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'products_count']
    search_fields = ['name']

    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('products')

    def products_count(self, obj):
        return obj.products.count()

    products_count.short_description = 'Products count'

    class Meta:
        verbose_name_plural = 'countries'


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'products_count']
    search_fields = ['name']

    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('products')

    def products_count(self, obj):
        return obj.products.count()

    products_count.short_description = 'Products count'

    class Meta:
        verbose_name_plural = 'manufacturers'


@admin.register(TeaCategory)
class TeaCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'products_count']
    search_fields = ['name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tea_attrs')

    def products_count(self, obj):
        return obj.tea_attrs.count()

    products_count.short_description = 'Количество товаров'


@admin.register(AccessoryType)
class AccessoryTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'products_count']
    search_fields = ['name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('accessory_attrs')

    def products_count(self, obj):
        return obj.accessory_attrs.count()

    products_count.short_description = 'Products count'


@admin.register(Aroma)
class AromaAdmin(admin.ModelAdmin):
    list_display = ['name', 'used_in_coffee', 'used_in_tea', 'total_usage']
    search_fields = ['name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('coffee_attrs', 'tea_attrs')

    def used_in_coffee(self, obj):
        return obj.coffee_attrs.count()

    def total_usage(self, obj):
        return obj.coffee_attrs.count() + obj.tea_attrs.count()

    def used_in_tea(self, obj):
        return obj.tea_attrs.count()

    used_in_coffee.short_description = 'In coffee'
    used_in_tea.short_description = 'In tea'
    total_usage.short_description = 'Total usage'


@admin.register(Additive)
class AdditiveAdmin(admin.ModelAdmin):
    list_display = ['name', 'used_in_coffee', 'used_in_tea', 'total_usage']
    search_fields = ['name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('coffee_attrs', 'tea_attrs')

    def used_in_coffee(self, obj):
        return obj.coffee_attrs.count()

    def used_in_tea(self, obj):
        return obj.tea_attrs.count()

    def total_usage(self, obj):
        return obj.coffee_attrs.count() + obj.tea_attrs.count()

    used_in_coffee.short_description = 'In coffee'
    used_in_tea.short_description = 'In tea'
    total_usage.short_description = 'Total usage'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'product_type_info',
        'manufacturer',
        'country',
        'variations_count',
        'total_stock',
        'available',
    ]
    list_filter = [
        'product_type',
        'available',
        # 'country',
        # 'manufacturer',
        ManufacturerFilter,
        CountryFilter
    ]
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

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('variations')

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

    def product_type_info(self, obj):
        return (f'{obj.get_product_type_display()} '
                f'{"☕" if obj.product_type == "coffee" else "🍵" if obj.product_type == "tea" else "🫖"}')

    def total_stock(self, obj):
        return sum(v.stock for v in obj.variations.all())

    variations_count.short_description = 'Variations'
    total_stock.short_description = 'Total stock'


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = [
        'product_link', 'text_description_of_count', 'price',
        'stock', 'available', 'stock_status'
    ]
    list_filter = ['available', 'product__product_type', StockFilter]
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


@admin.register(CoffeeAttribute)
class CoffeeAttributeAdmin(admin.ModelAdmin):
    form = CoffeeAttributeForm

    list_display = [
        'product',
        'coffee_type',
        'roast',
        'q_grading',
        'compositions_info',
        'aromas_info',
        'additives_info',
    ]
    list_filter = [
        'coffee_type',
        'roast',
        ('q_grading', NumericRangeFilterBuilder(title='Q-grading')),
        ("arabica_percent", NumericRangeFilterBuilder(title='Arabica (А) percent')),
        ("robusta_percent", NumericRangeFilterBuilder(title='Robusta (Р) percent')),
        ("liberica_percent", NumericRangeFilterBuilder(title='Liberica (Л) percent')),
        AromaFilter,
        AdditiveFilter,
    ]
    search_fields = ['product__name']
    filter_horizontal = ['aromas', 'additives']

    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('aromas', 'additives')

    def compositions_info(self, obj):
        return f'{obj.arabica_percent}% (А), {obj.robusta_percent}% (Р), {obj.liberica_percent}% (Л)'

    def aromas_info(self, obj):
        return ", ".join([aromas.name for aromas in obj.aromas.all()])

    def additives_info(self, obj):
        return ", ".join([additives.name for additives in obj.additives.all()])

    def q_grading(self, obj):
        return obj.q_grading

    def arabica_percent(self, obj):
        return obj.arabica_percent

    def robusta_percent(self, obj):
        return obj.robusta_percent

    def liberica_percent(self, obj):
        return obj.liberica_percent


@admin.register(TeaAttribute)
class TeaAttributeAdmin(admin.ModelAdmin):
    list_display = ['product', 'tea_type', 'category', 'aromas_info', 'additives_info']
    list_filter = ['tea_type', TeaCategoryFilter, AromaFilter, AdditiveFilter]
    search_fields = ['product__name']
    filter_horizontal = ['aromas', 'additives']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('aromas', 'additives')

    def aromas_info(self, obj):
        return ", ".join([aromas.name for aromas in obj.aromas.all()])

    def additives_info(self, obj):
        return ", ".join([additives.name for additives in obj.additives.all()])


@admin.register(AccessoryAttribute)
class AccessoryAttributeAdmin(admin.ModelAdmin):
    list_display = ['product', 'accessory_type', 'volume']
    list_filter = ['accessory_type']
    search_fields = ['product__name']
