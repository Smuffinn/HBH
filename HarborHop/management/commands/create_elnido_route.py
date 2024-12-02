from django.core.management.base import BaseCommand
from django.utils import timezone
from HarborHop.models import Port, Route, Vessel, Schedule
from decimal import Decimal
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates El Nido route with schedules'

    def handle(self, *args, **kwargs):
        try:
            # Create ports
            manila_port, _ = Port.objects.get_or_create(
                name='Manila Port',
                defaults={'capacity': 1000}
            )
            
            elnido_port, _ = Port.objects.get_or_create(
                name='El Nido Port',
                defaults={'capacity': 400}
            )
            
            # Create vessel (updated to match your model)
            vessel, _ = Vessel.objects.get_or_create(
                name='El Nido Explorer',
                defaults={
                    'current_port': 'Manila Port',
                    'destination_port': 'El Nido Port',
                    'seating_capacity': 200
                }
            )
            
            # Create route
            route, _ = Route.objects.get_or_create(
                departure_port=manila_port,
                arrival_port=elnido_port,
                defaults={
                    'base_price': Decimal('1999.00'),
                    'distance': 580.00,
                    'duration': timedelta(hours=12),
                    'is_active': True
                }
            )

            # Create schedules for the next 7 days
            today = timezone.now()
            for i in range(7):
                day = today + timedelta(days=i)
                # Morning schedule - 7 AM
                morning_departure = day.replace(hour=7, minute=0, second=0, microsecond=0)
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
            
            self.stdout.write(self.style.SUCCESS('Successfully created El Nido route'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))