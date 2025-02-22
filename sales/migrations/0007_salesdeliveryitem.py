# Generated by Django 5.1.3 on 2024-11-29 15:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0003_recipe_description'),
        ('sales', '0006_salesorder_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesDeliveryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='出库数量')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('delivery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.salesdelivery', verbose_name='销售出库')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.product', verbose_name='产品')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='更新人')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
