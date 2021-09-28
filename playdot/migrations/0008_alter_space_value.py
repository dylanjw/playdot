# Generated by Django 3.2.7 on 2021-09-27 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('playdot', '0007_rename_metadata_gamedata_meta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='space',
            name='value',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='spaces', to='playdot.piece'),
        ),
    ]