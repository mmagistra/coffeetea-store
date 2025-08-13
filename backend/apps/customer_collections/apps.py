from django.apps import AppConfig


class CustomerCollectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.customer_collections'

    def ready(self):
        import apps.customer_collections.signals
