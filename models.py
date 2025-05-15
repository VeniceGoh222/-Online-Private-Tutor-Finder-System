from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone
from datetime import date

# Create your models here.

class User(AbstractUser):
    USER_ROLES = [
        ('PARENT', 'Parent'),
        ('TUTOR', 'Tutor'),
        ('STAFF', 'Staff'),
        ('ADMIN', 'Admin'),
    ]

    PROFILE_STATUS = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('PENDING', 'Pending'),
    ]

    user_id = models.CharField(max_length=10, unique=True)
    user_phone_num = models.CharField(max_length=15)
    user_role = models.CharField(max_length=20, choices=USER_ROLES)
    profile_status = models.CharField(max_length=20, choices=PROFILE_STATUS, default='PENDING')

    class Meta:
        db_table = 'User'

    def __str__(self):
        return f"{self.username} ({self.get_user_role_display()})"

class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    staff_name = models.CharField(max_length=150)
    staff_email = models.EmailField(unique=True)
    staff_password = models.CharField(max_length=128)
    staff_phone = models.CharField(max_length=15)

    def __str__(self):
        return self.staff_name

    class Meta:
        db_table = 'Staff'

class Administrator(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=150)
    admin_email = models.EmailField(unique=True)
    admin_password = models.CharField(max_length=128)
    admin_phone = models.CharField(max_length=15)

    def __str__(self):
        return self.admin_name

    class Meta:
        db_table = 'Administrator'

class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    education_level = models.CharField(max_length=100)
    subject_taught = models.CharField(max_length=100)
    tutor_name = models.CharField(max_length=100)
    certificate = models.FileField(upload_to='certificates/', null=True, blank=True)

    def __str__(self):
        return self.tutor_name

    def save(self, *args, **kwargs):
        # Delete old certificate if it exists and a new one is being uploaded
        if self.pk:
            try:
                old_instance = Tutor.objects.get(pk=self.pk)
                if old_instance.certificate and self.certificate != old_instance.certificate:
                    old_instance.certificate.delete(save=False)
            except Tutor.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the certificate file when the Tutor instance is deleted
        if self.certificate:
            self.certificate.delete(save=False)
        super().delete(*args, **kwargs)

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    parent_name = models.CharField(max_length=100)
    child_name = models.CharField(max_length=100)
    child_age = models.IntegerField()
    child_level = models.CharField(max_length=100)
    favorite_tutor_id = models.CharField(max_length=100, null=True, blank=True)
    favorite_time_slot = models.CharField(max_length=100, null=True, blank=True)
    favorite_class_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.parent_name

class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default='')
    description = models.TextField(default='')
    subject = models.CharField(max_length=100, default='')
    level = models.CharField(max_length=20, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    time_slots = models.JSONField(default=list)  # Store time slots as JSON array
    capacity = models.IntegerField(default=1)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, blank=True)
    session_time = models.DateTimeField(null=True, blank=True)  # For actual booked sessions

    class Meta:
        db_table = 'additem_schedule'

    def __str__(self):
        return f"{self.subject} by {self.tutor.tutor_name}"

class Class(models.Model):
    class_id = models.AutoField(primary_key=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    session_time = models.DateTimeField(null=True, blank=True)  # Optional field for session time
    price = models.DecimalField(max_digits=10, decimal_places=2)
    student_level = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    time_slots = models.JSONField(default=dict)  # Store time slots as a dictionary of lists
    capacity = models.IntegerField(default=1)  # Add the capacity field

    class Meta:
        db_table = 'additem_classes'  # Specify the name of the table

    def __str__(self):
        return f"{self.subject_name} ({self.tutor.tutor_name})"

class FavoriteTutor(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='favorite_tutors_list')
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    selected_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=255)
    end_time = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'additem_favoriteTutors'

    def __str__(self):
        return f"{self.parent.parent_name} - {self.tutor.tutor_name} - {self.start_time} - {self.end_time}"

class Booking(models.Model):
    BOOKING_STATUS = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    booking_id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    session_time = models.DateTimeField()
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.booking_id}: {self.parent.parent_name} with {self.tutor.tutor_name}"

    @property
    def price(self):
        """Retrieve price from the associated Class model"""
        try:
            class_obj = Class.objects.get(tutor=self.tutor, subject_name=self.subject_name)
            return class_obj.price
        except Class.DoesNotExist:
            return None

class Feedback(models.Model):
    FEEDBACK_STATUS = [
        ('PENDING', 'Pending'),
        ('VALID', 'Valid'),
        ('INVALID', 'Invalid'),
        ('RESOLVED', 'Resolved'),
    ]
    
    feedback_id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    session_time = models.DateTimeField(null=True, blank=True)
    flagged = models.BooleanField(default=False)
    comments = models.TextField()
    status = models.CharField(max_length=20, choices=FEEDBACK_STATUS, default='PENDING')
    staff_response = models.TextField(null=True, blank=True)
    staff_notes = models.TextField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_feedback')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    PAYMENT_METHODS = [
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('e_wallet', 'E-Wallet'),
    ]
    
    payment_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='bank_transfer')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Payment'

    def __str__(self):
        return f"Payment {self.payment_id} - {self.booking.booking_id} - {self.payment_status}"

class Communication(models.Model):
    chat_id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    message = models.TextField()  # Field for storing the message text
    user_role = models.CharField(max_length=20, choices=User.USER_ROLES, default='PARENT')  # Field to identify message sender
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        db_table = 'additem_communication'
        unique_together = ['parent', 'tutor', 'message', 'user_role', 'created_at']
    
    def __str__(self):
        return self.message

class SupportAssistance(models.Model):
    QUERY_STATUS = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]
    
    query_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query_details = models.TextField()
    response = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=QUERY_STATUS)

class Notification(models.Model):
    NOTIFICATION_STATUS = [
        ('SCHEDULED', 'Scheduled'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed')
    ]

    TARGET_CHOICES = [
        ('ALL', 'All Users'),
        ('PARENT', 'Parents'),
        ('TUTOR', 'Tutors'),
        ('STAFF', 'Staff')
    ]

    DELIVERY_METHODS = [
        ('IN_APP', 'In-App'),
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('ALL', 'All Methods')
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    target_audience = models.CharField(max_length=20, choices=TARGET_CHOICES)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS, default='IN_APP')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=NOTIFICATION_STATUS, default='SCHEDULED')
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.target_audience} ({self.status})"

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.notification.title}"

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


@receiver(post_migrate)
def create_initial_staff_and_admin(sender, **kwargs):
    if sender.name == 'additem':  # Only run for our app
        # Create Staff if they don't exist
        if Staff.objects.count() == 0:
            Staff.objects.create(
                staff_name="staff1",
                staff_email="staff1@gmail.com",
                staff_password="staff123",
                staff_phone="1234567890"
            )


            Staff.objects.create(
                staff_name="staff2",
                staff_email="staff2@gmail.com",
                staff_password="staff456",
                staff_phone="0987654321"
            )

            print("Created initial staff members")

        # Create Administrators if they don't exist
        if Administrator.objects.count() == 0:
            Administrator.objects.create(
                admin_name="admin1",
                admin_email="admin1@gmail.com",
                admin_password="admin123",
                admin_phone="1112223333"
            )


            Administrator.objects.create(
                admin_name="admin2",
                admin_email="admin2@gmail.com",
                admin_password="admin456",
                admin_phone="4445556666"
            )

            print("Created initial administrators")

    
