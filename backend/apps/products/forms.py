from django import forms
from django.core.exceptions import ValidationError

from .models import CoffeeAttribute
from .validators import validate_percentage_sum_equals_100


class CoffeeAttributeForm(forms.ModelForm):
    class Meta:
        model = CoffeeAttribute
        fields = '__all__'

    def full_clean(self):
        super().full_clean()
        print(self.cleaned_data)
        arabica_percent = self.cleaned_data.get('arabica_percent')
        robusta_percent = self.cleaned_data.get('robusta_percent')
        liberica_percent = self.cleaned_data.get('liberica_percent')
        try:
            validate_percentage_sum_equals_100(arabica_percent, robusta_percent, liberica_percent)
        except ValidationError as e:
            self.add_error('arabica_percent', e)
            self.add_error('robusta_percent', e)
            self.add_error('liberica_percent', e)


class CoffeeAttributeInlineForm(forms.ModelForm):
    class Meta:
        model = CoffeeAttribute
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        arabica_percent = cleaned_data.get('arabica_percent')
        robusta_percent = cleaned_data.get('robusta_percent')
        liberica_percent = cleaned_data.get('liberica_percent')
        try:
            validate_percentage_sum_equals_100(arabica_percent, robusta_percent, liberica_percent)
        except ValidationError as e:
            self.add_error('arabica_percent', e)
            self.add_error('robusta_percent', e)
            self.add_error('liberica_percent', e)
        return cleaned_data
