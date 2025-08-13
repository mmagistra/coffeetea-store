from django.urls import path
from .views import (
    get_variations_for_product
)


app_name = 'products'

urlpatterns = [
    path('get-variations/<int:product_id>/',
         get_variations_for_product, name='get_variations_for_product'),
]
