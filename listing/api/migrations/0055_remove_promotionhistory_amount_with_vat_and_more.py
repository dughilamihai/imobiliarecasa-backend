# Generated by Django 5.1.2 on 2025-02-07 04:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0054_promotionhistory_payment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotionhistory',
            name='amount_with_vat',
        ),
        migrations.RemoveField(
            model_name='promotionhistory',
            name='amount_without_vat',
        ),
        migrations.RemoveField(
            model_name='promotionhistory',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='promotionhistory',
            name='vat_amount',
        ),
        migrations.RemoveField(
            model_name='promotionhistory',
            name='vat_rate',
        ),
    ]
