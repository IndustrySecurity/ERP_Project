# Generated by Django 4.2.17 on 2025-01-23 16:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0006_remove_productionline_capacity_and_more'),
        ('production', '0003_warehousedproduct'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='数量')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.product', verbose_name='产品')),
                ('production_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='production.productionorder', verbose_name='生产工单')),
            ],
        ),
    ]
