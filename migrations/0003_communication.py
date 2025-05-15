from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('additem', '0002_delete_communication'),
    ]

    operations = [
        migrations.CreateModel(
            name='Communication',
            fields=[
                ('chat_id', models.AutoField(primary_key=True, serialize=False)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='additem.parent')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='additem.tutor')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='additem.user')),
            ],
            options={
                'db_table': 'additem_communication',
                'ordering': ['created_at'],
            },
        ),
    ]
