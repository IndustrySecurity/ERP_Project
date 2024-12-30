# Generated by Django 5.1.3 on 2024-11-28 08:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('master_data', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WarehouseLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='仓库位置名称')),
                ('description', models.TextField(blank=True, verbose_name='描述')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='更新人')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('category', models.CharField(choices=[('material', '原材料'), ('product', '产品')], max_length=20, verbose_name='类别')),
                ('item', models.CharField(max_length=255, verbose_name='调拨项')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='调拨数量')),
                ('remarks', models.TextField(blank=True, verbose_name='备注')),
                ('date', models.DateField(auto_now_add=True, verbose_name='调拨日期')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='更新人')),
                ('from_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers_from', to='warehouse.warehouselocation', verbose_name='调拨自')),
                ('to_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers_to', to='warehouse.warehouselocation', verbose_name='调拨到')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='库存数量')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.product', verbose_name='产品')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='更新人')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.warehouselocation', verbose_name='仓库位置')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MaterialStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='库存数量')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.material', verbose_name='原材料')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='更新人')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.warehouselocation', verbose_name='仓库位置')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InventoryCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('before_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='盘点前数量')),
                ('after_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='盘点后数量')),
                ('variance', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='盈亏数量')),
                ('date', models.DateField(auto_now_add=True, verbose_name='盘点日期')),
                ('remarks', models.TextField(blank=True, verbose_name='备注')),
                ('category', models.CharField(choices=[('material', '原材料'), ('product', '成品')], default='material', max_length=50, verbose_name='类别')),
                ('item', models.CharField(blank=True, max_length=255, verbose_name='盘点项目')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='更新人')),
                ('material_stock', models.ManyToManyField(blank=True, to='warehouse.materialstock', verbose_name='原材料库存')),
                ('product_stock', models.ManyToManyField(blank=True, to='warehouse.productstock', verbose_name='产品库存')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.warehouselocation', verbose_name='仓库位置')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]