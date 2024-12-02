from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Port(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Vessel(models.Model):
    name = models.CharField(max_length=100)
    current_port = models.CharField(max_length=100)
    destination_port = models.CharField(max_length=100)
    seating_capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Route(models.Model):
    departure_port = models.ForeignKey(Port, on_delete=models.CASCADE, related_name='departure_routes')
    arrival_port = models.ForeignKey(Port, on_delete=models.CASCADE, related_name='arrival_routes')
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    distance = models.DecimalField(max_digits=10, decimal_places=2, help_text="Distance in nautical miles")
    duration = models.DurationField(help_text="Expected journey duration")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['departure_port', 'arrival_port']

    def __str__(self):
        return f"{self.departure_port} to {self.arrival_port}"

class Schedule(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    available_seats = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[
        ('SCHEDULED', 'Scheduled'),
        ('BOARDING', 'Boarding'),
        ('DEPARTED', 'Departed'),
        ('ARRIVED', 'Arrived'),
        ('CANCELLED', 'Cancelled'),
    ], default='SCHEDULED')

    def __str__(self):
        return f"{self.route} - {self.departure_time.strftime('%Y-%m-%d %H:%M')}"

class Booking(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed')
    ]

    # Passenger Information
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    # Booking Details
    schedule = models.ForeignKey(Schedule, on_delete=models.PROTECT)
    booking_reference = models.CharField(max_length=10, unique=True)
    number_of_passengers = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    package_type = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Price Details
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    taxes = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate a unique booking reference
            import random
            import string
            while True:
                reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not Booking.objects.filter(booking_reference=reference).exists():
                    self.booking_reference = reference
                    break

        # Ensure base_fare and taxes have default values if None
        if self.base_fare is None:
            self.base_fare = Decimal('0.00')
        if self.taxes is None:
            self.taxes = Decimal('0.00')

        # Calculate total amount
        self.total_amount = self.base_fare + self.taxes

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.name}"

    class Meta:
        ordering = ['-created_at']