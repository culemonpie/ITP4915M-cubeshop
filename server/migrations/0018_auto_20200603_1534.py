# Generated by Django 3.0.3 on 2020-06-03 15:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0017_auto_20200603_0331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='store',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='works_in', to='server.Store'),
        ),
    ]