# Generated by Django 5.1.2 on 2025-02-06 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0050_payment_promotionhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='promoted_days',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
