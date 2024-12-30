# Generated by Django 5.1.3 on 2024-11-28 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='客户名称')),
                ('contact_info', models.CharField(blank=True, max_length=255, verbose_name='联系方式')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='电子邮件')),
                ('address', models.TextField(blank=True, verbose_name='地址')),
                ('grade', models.CharField(choices=[('A', '一级客户'), ('B', '二级客户'), ('C', '三级客户')], default='C', max_length=1, verbose_name='客户等级')),
                ('company', models.CharField(blank=True, max_length=255, verbose_name='公司名称')),
                ('remarks', models.TextField(blank=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('material_number', models.CharField(blank=True, max_length=50, unique=True, verbose_name='料号')),
                ('name', models.CharField(max_length=255, verbose_name='原材料名称')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='单价')),
                ('capacity', models.CharField(blank=True, max_length=50, null=True, verbose_name='容量')),
                ('color', models.CharField(blank=True, max_length=50, null=True, verbose_name='颜色')),
                ('customer_supply', models.CharField(choices=[('客供', '客供'), ('非客供', '非客供')], default='非客供', max_length=10, verbose_name='客供/非客供')),
                ('technology', models.TextField(blank=True, null=True, verbose_name='工艺技术')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='备注')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MaterialCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='原材料类别')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('product_code', models.CharField(max_length=20, unique=True, verbose_name='产品编号')),
                ('name', models.CharField(max_length=255, verbose_name='产品名称')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='单价')),
                ('material', models.CharField(blank=True, max_length=255, null=True, verbose_name='容器材质')),
                ('capacity', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='容量')),
                ('technology', models.TextField(blank=True, null=True, verbose_name='工艺技术')),
                ('color', models.CharField(blank=True, max_length=50, null=True, verbose_name='颜色')),
                ('contract_date', models.DateField(blank=True, null=True, verbose_name='合同日期')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='备注')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='产品类别')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecipeMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='数量')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(max_length=255, verbose_name='供应商名称')),
                ('contact', models.CharField(blank=True, max_length=100, null=True, verbose_name='联系方式')),
                ('address', models.TextField(blank=True, null=True, verbose_name='地址')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]