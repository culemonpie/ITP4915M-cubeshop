# Generated by Django 3.0.3 on 2020-06-12 06:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0008_auto_20200611_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='owner',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='server.Tenant'),
            preserve_default=False,
        ),
    ]