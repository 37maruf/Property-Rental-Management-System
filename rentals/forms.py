from django import forms

from accounts.forms import BootstrapFormMixin

from .models import RentalRequest, Review


class RentalRequestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = RentalRequest
        fields = ('message',)
        widgets = {'message': forms.Textarea(attrs={
            'rows': 3, 'placeholder': 'Introduce yourself and say when you want to move in...'})}

    def __init__(self, *args, property=None, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.property = property
        self.tenant = tenant

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise forms.ValidationError('Please write at least 10 characters.')
        return message

    def clean(self):
        data = super().clean()
        if self.property is None or self.tenant is None:
            return data
        if self.property.owner_id == self.tenant.id:
            raise forms.ValidationError('You cannot request your own property.')
        if not self.property.is_available:
            raise forms.ValidationError('This property is not available.')
        if RentalRequest.objects.filter(property=self.property, tenant=self.tenant,
                                        status=RentalRequest.PENDING).exists():
            raise forms.ValidationError('You already have a pending request for this property.')
        return data


class ReviewForm(BootstrapFormMixin, forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[(i, f'{i} ★') for i in range(5, 0, -1)], coerce=int)

    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {'comment': forms.Textarea(attrs={'rows': 3})}
