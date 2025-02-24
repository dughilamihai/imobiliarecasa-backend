# Generated by Django 5.1.2 on 2025-02-15 17:53

import django.db.models.deletion
import django.utils.timezone
import django_ckeditor_5.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0059_privacypolicyhistory_current_content_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TermsPolicySection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_number', models.CharField(max_length=10)),
                ('title', models.CharField(max_length=255)),
                ('content', django_ckeditor_5.fields.CKEditor5Field()),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TermsPolicyHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_title', models.CharField(max_length=255)),
                ('old_content', django_ckeditor_5.fields.CKEditor5Field()),
                ('current_title', models.CharField(max_length=255)),
                ('current_content', django_ckeditor_5.fields.CKEditor5Field()),
                ('diff_title', models.TextField()),
                ('diff_content', models.TextField()),
                ('modified_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='api.termspolicysection')),
            ],
        ),
    ]
