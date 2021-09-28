# Generated by Django 3.2.7 on 2021-09-27 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('playdot', '0008_alter_space_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='space',
            name='value',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spaces', to='playdot.piece'),
        ),
    ]