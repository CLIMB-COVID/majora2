# Generated by Django 2.2.24 on 2022-01-05 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('majora2', '0142_auto_20211213_1312'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='publishedartifactgroup',
            options={'permissions': [('temp_can_read_pags_via_api', 'Can read published artifact groups via the API'), ('can_suppress_pags_via_api', 'Can suppress their own published artifact group via the API'), ('can_suppress_any_pags_via_api', 'Can suppress any published artifact group via the API')]},
        ),
    ]
