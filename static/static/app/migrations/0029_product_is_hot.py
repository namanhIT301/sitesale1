# Generated by Django 5.0.1 on 2024-07-19 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_remove_order_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_hot',
            field=models.BooleanField(default=False),
        ),
    ]