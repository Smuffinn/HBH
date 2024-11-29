from django import forms
from django.contrib.auth.models import User
from .models import Booking

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




class LoginForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['vessel', 'departure_port', 'arrival_port', 'price']
        widgets = {
            'price': forms.NumberInput(attrs={'step': 0.01}),
        }