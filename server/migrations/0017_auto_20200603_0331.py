# Generated by Django 3.0.3 on 2020-06-03 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0016_auto_20200602_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='change',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=6),
        ),
        migrations.AlterField(
            model_name='showcaserental',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]