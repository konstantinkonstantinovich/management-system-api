from django import forms
from api.models import VerificationCode
from django.utils import timezone


class ConfirmationForm(forms.ModelForm):
    class Meta:
        model = VerificationCode
        fields = ['code']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control mb-2'})
        }

    def clean(self):
        if self.instance.code != self.cleaned_data.get('code'):
            raise forms.ValidationError('Invalid code')

        if timezone.now() > self.instance.code_expiration_date:
            raise forms.ValidationError('Code expired')

        return self.cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.code = None
        instance.code_expiration_date = None
        user = instance.user
        user.is_verified = True
        if commit:
            instance.save()
            user.save()
        return instance
