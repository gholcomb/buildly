# Generated by Django 2.0.7 on 2018-10-10 09:27

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogicModule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_uuid', models.CharField(default=uuid.uuid4, max_length=255, unique=True, verbose_name='Logic Module UUID')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Logic Module Name')),
                ('description', models.TextField(blank=True, max_length=765, null=True, verbose_name='Description/Notes')),
                ('endpoint', models.CharField(blank=True, max_length=255, null=True)),
                ('github_repo', models.CharField(blank=True, max_length=500, null=True)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('edit_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Logic Modules',
                'ordering': ('name',),
            },
        ),
    ]
