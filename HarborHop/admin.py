from django.contrib import admin
from .models import Port, Vessel, Route, Schedule, Booking

@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'is_active')
    search_fields = ('name',)

@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_port', 'destination_port', 'seating_capacity')
    search_fields = ('name',)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('departure_port', 'arrival_port', 'base_price', 'distance', 'duration', 'is_active')
    list_filter = ('is_active', 'departure_port', 'arrival_port')
    search_fields = ('departure_port__name', 'arrival_port__name')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('route', 'vessel', 'departure_time', 'arrival_time', 'available_seats', 'status')
    list_filter = ('status', 'route', 'vessel')
    search_fields = ('route__departure_port__name', 'route__arrival_port__name')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'name', 'schedule', 'status', 'total_amount')
    list_filter = ('status', 'package_type')
    search_fields = ('name', 'email', 'booking_reference')