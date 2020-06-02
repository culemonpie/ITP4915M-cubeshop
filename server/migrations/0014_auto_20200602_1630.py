# Generated by Django 3.0.3 on 2020-06-02 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0013_auto_20200602_1620'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventory',
            options={'verbose_name_plural': 'Inventories'},
        ),
        migrations.AddConstraint(
            model_name='inventory',
            constraint=models.UniqueConstraint(fields=('from_stock', 'from_showcase'), name='unique_stock_per_showcase'),
        ),
    ]
