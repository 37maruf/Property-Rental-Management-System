from django.core.management.base import BaseCommand

from accounts.models import User
from properties.models import Property


class Command(BaseCommand):
    help = 'Create demo owner, tenant and a few properties (password: demo12345)'

    def handle(self, *args, **options):
        owner, _ = User.objects.get_or_create(
            username='demo_owner', defaults={'email': 'owner@example.com', 'role': 'owner'})
        tenant, _ = User.objects.get_or_create(
            username='demo_tenant', defaults={'email': 'tenant@example.com', 'role': 'tenant'})
        for u in (owner, tenant):
            u.set_password('demo12345')
            u.save()

        samples = [
            ('Sunny 2BR Apartment', 'apartment', 'Dhanmondi, Dhaka', 25000, 2, 2),
            ('Cozy Single Room', 'room', 'Barisal Sadar', 6000, 1, 1),
            ('Family House with Garden', 'house', 'Gulshan, Dhaka', 55000, 4, 3),
            ('Modern Office Space', 'office', 'Agrabad, Chattogram', 40000, 0, 1),
        ]
        for title, ptype, loc, rent, bed, bath in samples:
            Property.objects.get_or_create(
                title=title, owner=owner,
                defaults=dict(description=f'{title} in a great location. Close to shops and transport.',
                              property_type=ptype, location=loc, monthly_rent=rent,
                              bedrooms=bed, bathrooms=bath))
        self.stdout.write(self.style.SUCCESS('Demo data ready. Logins: demo_owner / demo_tenant, password demo12345'))
