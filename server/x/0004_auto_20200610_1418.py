# Generated by Django 3.0.3 on 2020-06-10 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0003_receipt_discount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchase',
            old_name='stock_code',
            new_name='stock_id',
        ),
    ]