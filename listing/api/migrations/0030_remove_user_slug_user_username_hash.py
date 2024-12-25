# Generated by Django 5.1.2 on 2024-12-25 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_alter_user_managers_user_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='slug',
        ),
        migrations.AddField(
            model_name='user',
            name='username_hash',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True),
        ),
    ]