from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_initial_staff_and_admin(sender, **kwargs):
    if sender.name == 'additem':  # Only run for our app
        from .models import Staff, Administrator  # Import here to avoid circular import
        
        # Create Staff if they don't exist
        if Staff.objects.count() == 0:
            Staff.objects.create(
                staff_name="John Smith",
                staff_email="john.smith@example.com",
                staff_password="staff123",
                staff_phone="1234567890"
            )
            print("Created initial staff members")

        # Create Administrators if they don't exist
        if Administrator.objects.count() == 0:
            Administrator.objects.create(
                admin_name="Admin One",
                admin_email="admin1@example.com",
                admin_password="admin123",
                admin_phone="1112223333"
            )
            print("Created initial administrators")