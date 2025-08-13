from django import forms
from django.core.exceptions import ValidationError

from .models import CartItem, WishlistItem, Cart, Wishlist

from apps.products.models import Product, Variation
from .validators import validate_only_one_field_used


class CartItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        label='Товар',
        empty_label='Выберите товар'
    )

    class Meta:
        model = CartItem
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.variation:
            self.fields['product'].initial = self.instance.variation.product
            self.fields['variation'].queryset = Variation.objects.filter(
                product=self.instance.variation.product
            ).select_related('product')
        else:
            self.fields['variation'].queryset = Variation.objects.none()

        self.fields['product'].widget.attrs.update({
            'class': 'product-selector',
            'onchange': 'updateVariations(this)',
            'style': 'width: 200px;'
        })

        self.fields['variation'].widget.attrs.update({
            'class': 'variation-selector',
            'style': 'width: 250px;'
        })

        self.fields['variation'].empty_label = 'Сначала выберите товар'

    def full_clean(self):
        if hasattr(self, 'data') and self.data:
            variation_field_name = self.add_prefix('variation')
            variation_id = self.data.get(variation_field_name)

            if variation_id:
                try:
                    selected_variation = Variation.objects.get(pk=variation_id)
                    self.fields['variation'].queryset = Variation.objects.filter(pk=variation_id)
                except Variation.DoesNotExist:
                    pass

        super().full_clean()

    def clean_variation(self):
        variation = self.cleaned_data.get('variation')
        product = self.cleaned_data.get('product')

        if variation and product:
            if variation.product != product:
                raise forms.ValidationError('Выбранная вариация не принадлежит выбранному товару')

        return variation

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        variation = cleaned_data.get('variation')

        if product and not variation:
            raise forms.ValidationError('Необходимо выбрать вариацию для товара')

        return cleaned_data


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = '__all__'

    def clean_session_key(self):
        session_key = self.cleaned_data.get('session_key')
        user = self.cleaned_data.get('user')

        if session_key and user:
            raise forms.ValidationError('Пользователь и сессия не могут быть заданы одновременно')

        if not session_key and not user:
            raise forms.ValidationError('Пользователь или сессия должны быть заданы')

        return session_key


class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = '__all__'

    def full_clean(self):
        super().full_clean()
        obj = self.instance

        try:
            validate_only_one_field_used(obj, 'session_key', 'user')
        except ValidationError as e:
            self.add_error('session_key', e)
            self.add_error('user', e)
