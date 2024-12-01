
from django.core.management.base import BaseCommand
from HarborHop.models import Port, Route
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates test data for Boracay routes'

    def handle(self, *args, **kwargs):
        # Create ports
        manila_port, _ = Port.objects.get_or_create(
            name='Manila Port',
            defaults={'capacity': 1000}
        )
        
        boracay_port, _ = Port.objects.get_or_create(
            name='Boracay Port',
            defaults={'capacity': 500}
        )
        
        # Create route
        route, created = Route.objects.get_or_create(
            departure_port=manila_port,
            arrival_port=boracay_port,
            defaults={
                'base_price': 999.00,
                'distance': 100.00,
                'duration': timedelta(hours=4),
                'is_active': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created test data'))