# Generated by Django 5.1.2 on 2024-12-25 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_alter_user_is_active'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]