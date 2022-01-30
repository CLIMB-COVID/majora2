# Generated by Django 2.2.26 on 2022-01-30 00:50

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('majora2', '0145_auto_20220111_1736'),
    ]

    operations = [
        migrations.CreateModel(
            name='MajoraFact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('namespace', models.CharField(max_length=64)),
                ('key', models.CharField(max_length=64)),
                ('value_type', models.CharField(max_length=48)),
                ('value', models.CharField(blank=True, max_length=128, null=True)),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
