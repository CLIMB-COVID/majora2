# Generated by Django 2.2.26 on 2022-02-26 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('majora2', '0150_majoraartifactprocessrecord_unique_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='majoraartifactprocessrecord',
            name='unique_name',
            field=models.CharField(max_length=256, null=True, unique=True),
        ),
    ]
