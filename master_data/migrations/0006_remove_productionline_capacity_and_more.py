# Generated by Django 4.2.17 on 2025-01-18 06:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0005_productionline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productionline',
            name='capacity',
        ),
        migrations.RemoveField(
            model_name='productionline',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='productionline',
            name='status',
        ),
        migrations.RemoveField(
            model_name='productionline',
            name='updated_at',
        ),
    ]
