# Generated by Django 3.0.3 on 2020-06-04 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0018_auto_20200603_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='purchase_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]