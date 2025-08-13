from django.db.models import signals
from django.dispatch import receiver

from .models import CoffeeAttribute, Product
from .validators import validate_percentage_sum_equals_100, validate_product_correct_attribute


@receiver(signals.pre_save, sender=CoffeeAttribute)
def coffee_attribute_pre_save(sender, instance, **kwargs):
    validate_percentage_sum_equals_100(
        instance.arabica_percent, instance.robusta_percent, instance.liberica_percent
    )

@receiver(signals.pre_save, sender=Product)
def product_pre_save(sender, instance, **kwargs):
    validate_product_correct_attribute(instance)
