# Generated by Django 5.0.3 on 2024-05-28 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_alter_inventory_status_alter_notification_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='expiry_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
