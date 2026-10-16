from django import forms

from accounts.forms import BootstrapFormMixin

from .models import Property


class PropertyForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Property
        fields = ('title', 'description', 'property_type', 'location', 'monthly_rent',
                  'bedrooms', 'bathrooms', 'image', 'is_available')
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def clean_monthly_rent(self):
        rent = self.cleaned_data['monthly_rent']
        if rent <= 0:
            raise forms.ValidationError('Monthly rent must be greater than zero.')
        return rent

    def clean_bedrooms(self):
        value = self.cleaned_data['bedrooms']
        if value > 50:
            raise forms.ValidationError('That number of bedrooms looks wrong.')
        return value

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'size') and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Image must be smaller than 5 MB.')
        return image


class PropertySearchForm(BootstrapFormMixin, forms.Form):
    location = forms.CharField(required=False, label='Location',
                               widget=forms.TextInput(attrs={'placeholder': 'e.g. Dhaka'}))
    property_type = forms.ChoiceField(required=False, label='Type',
                                      choices=[('', 'All types')] + Property.TYPE_CHOICES)
    min_rent = forms.DecimalField(required=False, min_value=0, label='Min rent')
    max_rent = forms.DecimalField(required=False, min_value=0, label='Max rent')

    def clean(self):
        data = super().clean()
        low, high = data.get('min_rent'), data.get('max_rent')
        if low is not None and high is not None and low > high:
            raise forms.ValidationError('Min rent cannot be greater than max rent.')
        return data
