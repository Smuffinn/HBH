from django.core.management.base import BaseCommand
from HarborHop.models import Port, Vessel, Route, Schedule
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Sets up initial data for booking system'

    def handle(self, *args, **kwargs):
        # Create Ports
        ports_data = [
            {'name': 'Manila Port', 'capacity': 1000},
            {'name': 'Cebu Port', 'capacity': 800},
            {'name': 'Boracay Port', 'capacity': 500},
            {'name': 'Siargao Port', 'capacity': 300},
            {'name': 'El Nido Port', 'capacity': 400},
            {'name': 'Coron Port', 'capacity': 350},
        ]

        ports = {}
        for port_data in ports_data:
            port, created = Port.objects.get_or_create(
                name=port_data['name'],
                defaults={'capacity': port_data['capacity']}
            )
            ports[port.name] = port
            self.stdout.write(f'{"Created" if created else "Found"} port: {port.name}')

        # Create Vessels
        vessels_data = [
            {'name': 'Ocean Star', 'seating_capacity': 200},
            {'name': 'Island Voyager', 'seating_capacity': 150},
            {'name': 'Sea Explorer', 'seating_capacity': 180},
            {'name': 'Pearl Navigator', 'seating_capacity': 120},
        ]

        vessels = []
        for vessel_data in vessels_data:
            vessel, created = Vessel.objects.get_or_create(
                name=vessel_data['name'],
                defaults={
                    'seating_capacity': vessel_data['seating_capacity'],
                    'current_port': 'Manila Port',
                    'destination_port': 'Cebu Port'
                }
            )
            vessels.append(vessel)
            self.stdout.write(f'{"Created" if created else "Found"} vessel: {vessel.name}')

        # Create Routes
        routes_data = [
            {
                'departure': 'Manila Port',
                'arrival': 'Cebu Port',
                'base_price': 2500,
                'distance': 355,
                'duration': datetime.timedelta(hours=22)
            },
            {
                'departure': 'Manila Port',
                'arrival': 'Boracay Port',
                'base_price': 3000,
                'distance': 280,
                'duration': datetime.timedelta(hours=18)
            },
            {
                'departure': 'Cebu Port',
                'arrival': 'Siargao Port',
                'base_price': 2800,
                'distance': 250,
                'duration': datetime.timedelta(hours=16)
            },
            {
                'departure': 'Manila Port',
                'arrival': 'El Nido Port',
                'base_price': 3500,
                'distance': 420,
                'duration': datetime.timedelta(hours=24)
            },
        ]

        for route_data in routes_data:
            route, created = Route.objects.get_or_create(
                departure_port=ports[route_data['departure']],
                arrival_port=ports[route_data['arrival']],
                defaults={
                    'base_price': route_data['base_price'],
                    'distance': route_data['distance'],
                    'duration': route_data['duration'],
                    'is_active': True
                }
            )
            self.stdout.write(f'{"Created" if created else "Found"} route: {route}')

            # Create return route
            reverse_route, created = Route.objects.get_or_create(
                departure_port=ports[route_data['arrival']],
                arrival_port=ports[route_data['departure']],
                defaults={
                    'base_price': route_data['base_price'],
                    'distance': route_data['distance'],
                    'duration': route_data['duration'],
                    'is_active': True
                }
            )
            self.stdout.write(f'{"Created" if created else "Found"} return route: {reverse_route}')

        # Create Schedules
        self.stdout.write('Creating schedules...')
        
        # Get all routes and vessels
        routes = Route.objects.all()
        vessels = Vessel.objects.all()
        
        # Create schedules for the next 7 days
        today = timezone.now()
        for day in range(7):
            schedule_date = today + datetime.timedelta(days=day)
            
            # Create 3 schedules per route per day
            departure_times = [
                schedule_date.replace(hour=8, minute=0, second=0),  # Morning
                schedule_date.replace(hour=13, minute=0, second=0), # Afternoon
                schedule_date.replace(hour=18, minute=0, second=0)  # Evening
            ]
            
            for route in routes:
                for departure_time in departure_times:
                    arrival_time = departure_time + route.duration
                    vessel = vessels[day % len(vessels)]  # Rotate through vessels
                    
                    schedule, created = Schedule.objects.get_or_create(
                        route=route,
                        vessel=vessel,
                        departure_time=departure_time,
                        defaults={
                            'arrival_time': arrival_time,
                            'available_seats': vessel.seating_capacity,
                            'status': 'SCHEDULED'
                        }
                    )
                    if created:
                        self.stdout.write(f'Created schedule: {schedule}')