from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('additem', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Communication',
        ),
    ]
