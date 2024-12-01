from django.contrib import admin
from .models import Route, Schedule, Booking, Vessel, Port

@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_port', 'destination_port', 'seating_capacity')
    search_fields = ('name', 'current_port', 'destination_port')
    list_filter = ('current_port', 'destination_port')

@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')
    search_fields = ('name',)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('departure_port', 'arrival_port', 'base_price', 'duration', 'is_active')
    list_filter = ('is_active', 'departure_port', 'arrival_port')
    search_fields = ('departure_port__name', 'arrival_port__name')
    list_editable = ('base_price', 'is_active')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('route', 'vessel', 'departure_time', 'arrival_time', 'available_seats', 'status')
    list_filter = ('status', 'departure_time', 'vessel')
    search_fields = ('route__departure_port__name', 'route__arrival_port__name', 'vessel__name')
    date_hierarchy = 'departure_time'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'name', 'schedule', 'number_of_passengers', 
                   'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'schedule__route__departure_port', 
                  'schedule__route__arrival_port')
    search_fields = ('booking_reference', 'name', 'email', 'phone_number')
    readonly_fields = ('booking_reference', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Passenger Information', {
            'fields': ('name', 'email', 'phone_number', 'gender', 'age')
        }),
        ('Booking Details', {
            'fields': ('schedule', 'booking_reference', 'number_of_passengers', 'status')
        }),
        ('Price Information', {
            'fields': ('base_fare', 'taxes', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )