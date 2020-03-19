# Generated by Django 2.2.10 on 2020-03-19 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('majora2', '0017_auto_20200319_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='biosampleartifact',
            name='secondary_identifier',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='biosourcesamplingprocess',
            name='source_sex',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
