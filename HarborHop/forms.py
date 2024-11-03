from django import forms
from django.contrib.auth.models import User
from .models import Passenger

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = [
            'name',
            'gender',
            'date_of_birth',
            'address',
            'email',
            'phone_number',
            'class_type',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'YYYY-MM-DD',
            }),
            'class_type': forms.Select(attrs={
                'required': 'required',
            }),
        }