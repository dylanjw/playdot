# Generated by Django 3.2.7 on 2021-09-26 19:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('playdot', '0005_auto_20210926_1844'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlaydotGameData',
            fields=[
                ('gamedata_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='playdot.gamedata')),
            ],
            bases=('playdot.gamedata',),
        ),
    ]
