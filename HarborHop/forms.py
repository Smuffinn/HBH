from django import forms 
from .models import Booking, Schedule
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from decimal import Decimal

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
        fields = [
            'name', 
            'email',
            'phone_number',
            'gender',
            'age',
            'schedule',
            'number_of_passengers'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'schedule': forms.Select(attrs={'class': 'form-control'}),
            'number_of_passengers': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        schedule = cleaned_data.get('schedule')
        passengers = cleaned_data.get('number_of_passengers', 1)

        if schedule and passengers:
            if schedule.available_seats < passengers:
                raise forms.ValidationError(
                    f"Only {schedule.available_seats} seats available for this schedule"
                )

        return cleaned_data

    def save(self, commit=True):
        booking = super().save(commit=False)
        schedule = self.cleaned_data['schedule']
        
        # Set price details
        booking.base_fare = schedule.route.base_price * self.cleaned_data['number_of_passengers']
        booking.taxes = booking.base_fare * Decimal('0.12')  # 12% tax example
        booking.total_amount = booking.base_fare + booking.taxes

        if commit:
            booking.save()
            # Update available seats
            schedule.available_seats -= booking.number_of_passengers
            schedule.save()

        return booking