from django import forms
from .models import Passenger

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
            'class_type',  # Include class type field
            'additional_name',
            'additional_gender',
            'additional_date_of_birth',
            'additional_address',
            'additional_email',
            'additional_phone',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',  # This gives a date picker in modern browsers
                'placeholder': 'YYYY-MM-DD',  # Help users know the format
            }),
            'additional_date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'YYYY-MM-DD',
            }),
            'class_type': forms.Select(attrs={
                'required': 'required',  # Make sure this field is required
            }),
        }
