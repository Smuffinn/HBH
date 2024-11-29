from django.db import models

# class Passenger(models.Model):
#     name = models.CharField(max_length=100)
#     gender = models.CharField(max_length=10, null=True, blank=True)
#     age = models.PositiveIntegerField(null=True, blank=True)
#     address = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=15, unique=True) 

#     def __str__(self):
#         return self.name

class Vessel(models.Model):
    name = models.CharField(max_length=100)
    current_port = models.CharField(max_length=100)
    destination_port = models.CharField(max_length=100)
    seating_capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Port(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Booking(models.Model):
    name = models.CharField(max_length=100, default="Unknown")
    gender = models.CharField(max_length=10, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, default="Unknown")
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    departure_port = models.ForeignKey(Port, on_delete=models.CASCADE, related_name="departure_tickets")
    arrival_port = models.ForeignKey(Port, on_delete=models.CASCADE, related_name="arrival_tickets")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_issued = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vessel', 'departure_port', 'arrival_port') 

    def __str__(self):
        return f"{self.vessel.name}"