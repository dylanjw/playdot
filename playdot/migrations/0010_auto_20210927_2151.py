# Generated by Django 3.2.7 on 2021-09-27 21:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('playdot', '0009_alter_space_value'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelPlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(max_length=200)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='playdot.gamedata')),
                ('playing_as', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='playdot.piece')),
            ],
        ),
        migrations.AddConstraint(
            model_name='channelplayer',
            constraint=models.UniqueConstraint(fields=('game', 'playing_as'), name='player_constraint'),
        ),
    ]
