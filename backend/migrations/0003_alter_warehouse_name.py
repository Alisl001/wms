# Generated by Django 5.0.3 on 2024-04-26 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_alter_warehouse_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouse',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
