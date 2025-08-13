from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.admin.filters import SimpleListFilter


class AromaFilter(AutocompleteFilter):
    title = 'Aromas'
    field_name = 'aromas'


class AdditiveFilter(AutocompleteFilter):
    title = 'Additives'
    field_name = 'additives'


class ManufacturerFilter(AutocompleteFilter):
    title = 'Manufacturer'
    field_name = 'manufacturer'


class CountryFilter(AutocompleteFilter):
    title = 'Country'
    field_name = 'country'


class TeaCategoryFilter(AutocompleteFilter):
    title = 'Tea category'
    field_name = 'category'


class StockRangeDescription:
    def __init__(self, lower_or_equal_then=0, more_or_equal_then=0, use_top_limit=False):
        self.lower_or_equal_then = lower_or_equal_then
        self.more_or_equal_then = more_or_equal_then
        self.use_top_limit = use_top_limit

    def decode_from_string(self, string):
        SRD = StockRangeDescription()
        if string[-1] == ')':
            SRD.use_top_limit = False
            SRD.more_or_equal_then = int(string.split(', ')[0][1:])
        else:
            SRD.use_top_limit = True
            SRD.lower_or_equal_then = int(string.split(', ')[0][1:])
            SRD.more_or_equal_then = int(string.split(', ')[1][:-1])
        return SRD

    def encode_to_string(self):
        return f'[{self.more_or_equal_then}, +inf)' \
            if not self.use_top_limit else f'[{self.lower_or_equal_then}, {self.more_or_equal_then}]'

    def __repr__(self):
        return self.encode_to_string()

    def __str__(self):
        return self.encode_to_string()


class StockFilter(SimpleListFilter):
    title = 'stock'
    parameter_name = 'stock_range'
    field_name = 'stock'

    def lookups(self, request, model_admin):
        return (
            (StockRangeDescription(lower_or_equal_then=0, more_or_equal_then=0, use_top_limit=True).encode_to_string()[:], 'Нет в наличии'),
            (StockRangeDescription(lower_or_equal_then=9, more_or_equal_then=1, use_top_limit=True).encode_to_string(), 'Мало'),
            (StockRangeDescription(lower_or_equal_then=-1, more_or_equal_then=10, use_top_limit=False).encode_to_string(), 'В наличии'),
        )

    def queryset(self, request, queryset):
        stock_range = self.value()
        if stock_range:
            stock_range = StockRangeDescription().decode_from_string(stock_range)
            if not stock_range.use_top_limit:
                queryset = queryset.filter(stock__gte=stock_range.more_or_equal_then)
            else:
                queryset = queryset.filter(stock__gte=stock_range.more_or_equal_then, stock__lte=stock_range.lower_or_equal_then)
        return queryset
