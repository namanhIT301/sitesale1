# Generated by Django 5.0.1 on 2024-07-21 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0042_delete_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
