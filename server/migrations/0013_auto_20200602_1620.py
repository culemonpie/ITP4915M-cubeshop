# Generated by Django 3.0.3 on 2020-06-02 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0012_store_showcase_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='inventory_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='showcase',
            name='showcase_id',
            field=models.CharField(blank=True, max_length=255, primary_key=True, serialize=False),
        ),
    ]
