# Generated by Django 2.2.13 on 2020-11-10 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tatl', '0025_auto_20200828_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='tatlverb',
            name='extra_context',
            field=models.TextField(blank=True, default='{}', null=True),
        ),
    ]
