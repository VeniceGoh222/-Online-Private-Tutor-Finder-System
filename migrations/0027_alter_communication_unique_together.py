# Generated by Django 5.1.5 on 2025-02-11 15:43

from django.db import migrations
from django.db.models import Min

def remove_duplicates(apps, schema_editor):
    Communication = apps.get_model('additem', 'Communication')
    
    # Get all groups of duplicate records
    duplicates = (
        Communication.objects.values('parent_id', 'tutor_id', 'message', 'user_role')
        .annotate(min_chat_id=Min('chat_id'))
        .filter(created_at__isnull=False)
    )
    
    # For each group of duplicates
    for duplicate in duplicates:
        # Keep the oldest record (minimum chat_id) and delete the rest
        Communication.objects.filter(
            parent_id=duplicate['parent_id'],
            tutor_id=duplicate['tutor_id'],
            message=duplicate['message'],
            user_role=duplicate['user_role']
        ).exclude(chat_id=duplicate['min_chat_id']).delete()

def reverse_remove_duplicates(apps, schema_editor):
    # No need to reverse this operation
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('additem', '0026_remove_communication_sender_communication_user_role'),
    ]

    operations = [
        # First remove duplicates
        migrations.RunPython(remove_duplicates, reverse_remove_duplicates),
        # Then add the unique constraint
        migrations.AlterUniqueTogether(
            name='communication',
            unique_together={('parent', 'tutor', 'message', 'user_role', 'created_at')},
        ),
    ]
