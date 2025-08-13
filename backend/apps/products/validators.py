from django.core.exceptions import ValidationError


def validate_percentage_sum_equals_100(arabica_variety, robusta_variety, liberica_variety):
    if not all([arabica_variety, robusta_variety, liberica_variety]):
        return
    total_percentage = arabica_variety + robusta_variety + liberica_variety
    if total_percentage != 100:
        raise ValidationError("Sum of percentages must equal 100%")


def validate_product_correct_attribute(product_instance):
    if product_instance.product_type not in ['coffee', 'tea', 'accessory']:
        raise ValidationError('Product type is not correct')
    if not product_instance.product_type == 'coffee' and hasattr(product_instance, 'coffee_attribute'):
        raise ValidationError('Product with coffee type must have coffee attribute')
    if not product_instance.product_type == 'tea' and hasattr(product_instance, 'tea_attribute'):
        raise ValidationError('Product with tea type must not have tea attribute')
    if not product_instance.product_type == 'accessory' and hasattr(product_instance, 'accessory_attribute'):
        raise ValidationError('Product with accessory type must not have accessory attribute')

