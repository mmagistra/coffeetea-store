from .base import *

DEBUG = True
ALLOWED_HOSTS = []


INSTALLED_APPS = [
    *INSTALLED_APPS,
    # 3-rd party
    'debug_toolbar',
    # my apps
]

STATIC_URL = "static/"

# TEMPLATES = [
#     {
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "APP_DIRS": True,
#         # ...
#     }
# ]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    *MIDDLEWARE,
]

INTERNAL_IPS = [
    "127.0.0.1",
]
