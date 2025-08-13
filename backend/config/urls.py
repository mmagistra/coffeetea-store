from django.urls import include, path
from django.contrib import admin
from django.urls import path
from debug_toolbar.toolbar import debug_toolbar_urls

from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.urls')),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
