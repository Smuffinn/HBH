from django.core.management.base import BaseCommand
from HarborHop.models import Port, Route, Vessel, Schedule
from datetime import timedelta, datetime
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates a complete Boracay route with test data'

    def handle(self, *args, **kwargs):
        # Create ports
        manila_port, _ = Port.objects.get_or_create(
            name='Manila Port',
            defaults={'capacity': 1000}
        )
        
        boracay_port, _ = Port.objects.get_or_create(
            name='Caticlan Port',  # Using Caticlan as it's Boracay's main port
            defaults={'capacity': 500}
        )
        
        # Create vessel
        vessel, _ = Vessel.objects.get_or_create(
            name='FastCat Ferry 1',
            defaults={
                'current_port': 'Manila Port',
                'destination_port': 'Caticlan Port',
                'seating_capacity': 200
            }
        )
        
        # Create route
        route, _ = Route.objects.get_or_create(
            departure_port=manila_port,
            arrival_port=boracay_port,
            defaults={
                'base_price': 999.00,
                'distance': 315.00,  # Approximate nautical miles
                'duration': timedelta(hours=4),
                'is_active': True
            }
        )

        # Create some test schedules for the next 7 days
        for i in range(7):
            departure_time = timezone.now() + timedelta(days=i, hours=8)  # 8 AM departure
            arrival_time = departure_time + route.duration
            
            Schedule.objects.get_or_create(
                route=route,
                vessel=vessel,
                departure_time=departure_time,
                arrival_time=arrival_time,
                defaults={
                    'available_seats': vessel.seating_capacity,
                    'status': 'SCHEDULED'
                }
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created Boracay route with {Schedule.objects.filter(route=route).count()} schedules'
            )
        )