# Generated by Django 4.2.17 on 2025-02-12 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_paymentrecord_percentage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentrecord',
            name='percentage',
        ),
    ]
