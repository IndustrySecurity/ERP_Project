# Generated by Django 4.2.17 on 2025-01-18 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0003_alter_purchasereturn_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasereturn',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='purchase.purchaseorder', verbose_name='采购订单'),
        ),
    ]
