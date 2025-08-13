from django.urls import path
from django.urls.conf import include

urlpatterns = [
    # path('accounts/', include('apps.accounts.urls')),
    # path('common/', include('apps.common.urls')),
    # path('customer_collections/', include('apps.customer_collections.urls')),
    # path('notifications/', include('apps.notifications.urls')),
    # path('orders/', include('apps.orders.urls')),
    # path('payment/', include('apps.payment.urls')),
    path('products/', include('apps.products.urls')),
    # path('promotions/', include('apps.promotions.urls')),
    # path('reviews/', include('apps.reviews.urls')),
]