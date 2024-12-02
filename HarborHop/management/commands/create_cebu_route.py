
from django.core.management.base import BaseCommand
from HarborHop.models import Port, Route, Vessel, Schedule
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates a complete Cebu route with test data'

    def handle(self, *args, **kwargs):
        # Create ports
        manila_port, _ = Port.objects.get_or_create(
            name='Manila Port',
            defaults={'capacity': 1000}
        )
        
        cebu_port, _ = Port.objects.get_or_create(
            name='Cebu Port',
            defaults={'capacity': 800}
        )
        
        # Create vessel
        vessel, _ = Vessel.objects.get_or_create(
            name='Ocean Jet 2',
            defaults={
                'current_port': 'Manila Port',
                'destination_port': 'Cebu Port',
                'seating_capacity': 150
            }
        )
        
        # Create route
        route, _ = Route.objects.get_or_create(
            departure_port=manila_port,
            arrival_port=cebu_port,
            defaults={
                'base_price': 2499.00,
                'distance': 365.00,  # Approximate nautical miles
                'duration': timedelta(hours=5),
                'is_active': True
            }
        )

        # Create schedules for the next 7 days
        for i in range(7):
            # Morning schedule
            morning_departure = timezone.now() + timedelta(days=i, hours=8)  # 8 AM
            morning_arrival = morning_departure + route.duration
            
            Schedule.objects.get_or_create(
                route=route,
                vessel=vessel,
                departure_time=morning_departure,
                arrival_time=morning_arrival,
                defaults={
                    'available_seats': vessel.seating_capacity,
                    'status': 'SCHEDULED'
                }
            )
            
            # Afternoon schedule
            afternoon_departure = timezone.now() + timedelta(days=i, hours=13)  # 1 PM
            afternoon_arrival = afternoon_departure + route.duration
            
            Schedule.objects.get_or_create(
                route=route,
                vessel=vessel,
                departure_time=afternoon_departure,
                arrival_time=afternoon_arrival,
                defaults={
                    'available_seats': vessel.seating_capacity,
                    'status': 'SCHEDULED'
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully created Cebu route with schedules'))