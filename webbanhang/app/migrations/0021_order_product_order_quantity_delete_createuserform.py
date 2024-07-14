# Generated by Django 5.0.1 on 2024-07-14 14:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_remove_order_product_remove_order_quantity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.product'),
        ),
        migrations.AddField(
            model_name='order',
            name='quantity',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.DeleteModel(
            name='CreateUserForm',
        ),
    ]
