# Generated by Django 2.2.13 on 2021-01-11 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('majora2', '0135_majorametarecord_restricted'),
    ]

    operations = [
        migrations.AddField(
            model_name='institute',
            name='ena_assembly_opted',
            field=models.BooleanField(default=False),
        ),
    ]
