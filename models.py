"""
Definition of models.
"""

from django.db import models
from django.conf import settings

#sharing entity

class Item(models.Model):
    item_id = models.CharField(primary_key=True, max_length=10)
    item_name = models.TextField()
    item_description = models.TextField(null=True,default=None, blank=True)
    def __str__(self):
        return str(self.item_id)


class Notification(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]
    
    DELIVERY_CHOICES = [
        ('IN_APP', 'In-App Notification'),
        ('EMAIL', 'Email')
    ]
    
    AUDIENCE_CHOICES = [
        ('TUTORS', 'All Tutors'),
        ('PARENTS', 'All Parents'),
        ('ALL', 'All Users')
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=500)
    target_audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ['-created_at']
        db_table = 'app_notification'

class UserNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'app_user_notification'
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
