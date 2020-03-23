# Generated by Django 2.2.10 on 2020-03-23 16:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('majora2', '0026_auto_20200323_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='majoraartifactprocessrecord',
            name='bridge_artifact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bridge_process', to='majora2.MajoraArtifact'),
        ),
        migrations.AddField(
            model_name='majoraartifactprocessrecord',
            name='bridge_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bridge_process', to='majora2.MajoraArtifactGroup'),
        ),
    ]
