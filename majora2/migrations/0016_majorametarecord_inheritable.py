# Generated by Django 2.1.4 on 2019-08-20 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('majora2', '0015_majorametarecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='majorametarecord',
            name='inheritable',
            field=models.BooleanField(default=True),
        ),
    ]
