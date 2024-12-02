from django.core.management.base import BaseCommand
from django.utils import timezone
from HarborHop.models import Port, Route, Vessel, Schedule
from decimal import Decimal
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates Siargao route with schedules'

    def handle(self, *args, **kwargs):
        try:
            # Create ports
            manila_port, _ = Port.objects.get_or_create(
                name='Manila Port',
                defaults={'capacity': 1000}
            )
            
            siargao_port, _ = Port.objects.get_or_create(
                name='Siargao Port',
                defaults={'capacity': 300}
            )
            
            # Create vessel (updated to match your model)
            vessel, _ = Vessel.objects.get_or_create(
                name='Siargao Surfer Express',
                defaults={
                    'current_port': 'Manila Port',
                    'destination_port': 'Siargao Port',
                    'seating_capacity': 150
                }
            )
            
            # Create route
            route, _ = Route.objects.get_or_create(
                departure_port=manila_port,
                arrival_port=siargao_port,
                defaults={
                    'base_price': Decimal('1499.00'),
                    'distance': 750.00,
                    'duration': timedelta(hours=14),
                    'is_active': True
                }
            )

            # Create schedules for the next 7 days
            today = timezone.now()
            for i in range(7):
                day = today + timedelta(days=i)
                # Morning schedule - 8 AM
                morning_departure = day.replace(hour=8, minute=0, second=0, microsecond=0)
                morning_arrival = morning_departure + route.duration
                
                Schedule.objects.get_or_create(
                    route=route,
                    vessel=vessel,
                    departure_time=morning_departure,
                    defaults={
                        'arrival_time': morning_arrival,
                        'available_seats': vessel.seating_capacity,
                        'status': 'SCHEDULED'
                    }
                )

            self.stdout.write(self.style.SUCCESS('Successfully created Siargao route'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))