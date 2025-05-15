from django.core.management.base import BaseCommand
from additem.models import User

class Command(BaseCommand):
    help = 'Creates the default admin user'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin1').exists():
            User.objects.create_user(
                username='admin1',
                password='admin123',
                email='admin@example.com',
                user_role='ADMIN',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS('Successfully created admin user'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))
