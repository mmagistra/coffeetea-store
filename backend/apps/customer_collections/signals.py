from django.db.models import signals
from django.dispatch import receiver

from .models import Wishlist
from .validators import validate_only_one_field_used


@receiver(signals.pre_save, sender=Wishlist)
def cart_pre_save(sender, instance, **kwargs):
    validate_only_one_field_used(instance, 'user', 'session_key')