from django.core.exceptions import ValidationError


def validate_only_one_field_used(instance, first_field_name, second_field_name):
    if not hasattr(instance, first_field_name) or not hasattr(instance, second_field_name):
        return
    if not getattr(instance, first_field_name) and not getattr(instance, second_field_name):
        raise ValidationError('At least one field must be used.')

    if getattr(instance, first_field_name) and getattr(instance, second_field_name):
        raise ValidationError(
            f'Only one of {first_field_name} or {second_field_name} can be used.'
        )
