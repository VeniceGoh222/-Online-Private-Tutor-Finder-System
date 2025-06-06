# Generated by Django 5.1.5 on 2025-02-09 22:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('additem', '0012_parent_favorite_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedback',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_feedback', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='feedback',
            name='staff_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='staff_response',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('VALID', 'Valid'), ('INVALID', 'Invalid'), ('RESOLVED', 'Resolved')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='feedback',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_role',
            field=models.CharField(choices=[('PARENT', 'Parent'), ('TUTOR', 'Tutor'), ('STAFF', 'Staff'), ('ADMIN', 'Admin')], max_length=20),
        ),
    ]
