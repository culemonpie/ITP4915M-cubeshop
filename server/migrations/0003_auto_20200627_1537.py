# Generated by Django 3.0.3 on 2020-06-27 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_inventory_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenant',
            name='address',
            field=models.EmailField(max_length=255),
        ),
    ]