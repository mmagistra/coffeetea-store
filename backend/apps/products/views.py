from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from apps.products.models import Variation


@staff_member_required
def get_variations_for_product(request, product_id):
    try:
        variations = Variation.objects.filter(
            product_id=product_id
        ).select_related('product').values(
            'id', 'text_description_of_count', 'price'
        )

        return JsonResponse({
            'variations': list(variations),
            'success': True
        })
    except Exception as e:
        return JsonResponse({
            'variations': [],
            'success': False,
            'error': str(e)
        })


# class CoffeeAttributeAutocomplete(AutocompleteJsonView):
#     model_admin = None  # using my final class; can get away with None as well
#
#     def get_queryset(self):
#         # overriding to fix Django 3.2 upgrade issue (removed self.complex_query line)
#         qs = self.model_admin.get_queryset(self.request)
#         qs, search_use_distinct = self.model_admin.get_search_results(
#             self.request, qs, self.term
#         )
#         # qs = qs.filter() -> my custom search
#         if search_use_distinct:
#             qs = qs.distinct()
#         return qs
#     # def get_queryset(self):
#     #     """
#     #        your custom logic goes here.
#     #     """
#     #     queryset = super().get_queryset()
#     #     queryset = queryset.order_by('name')
#     #     return queryset

