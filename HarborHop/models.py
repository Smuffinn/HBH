from django.db import models

class Passenger(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, null=True, blank=True)    
    date_of_birth = models.DateField(null=True, blank=True)  # No default, should be filled by user
    address = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    class_type = models.CharField(max_length=20, null=True, blank=True)  # Make it nullable
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Make it nullable

    # Fields for additional passengers
    additional_name = models.CharField(max_length=100, blank=True, null=True)
    additional_gender = models.CharField(max_length=10, blank=True, null=True)
    additional_date_of_birth = models.DateField(blank=True, null=True)
    additional_address = models.CharField(max_length=255, blank=True, null=True)
    additional_email = models.EmailField(blank=True, null=True)
    additional_phone = models.CharField(max_length=15, blank=True, null=True)
    additional_class_type = models.CharField(max_length=20, null=True, blank=True)  # Make it nullable
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Make it nullable

    def __str__(self):
        return self.name
