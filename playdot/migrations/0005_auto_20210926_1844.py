# Generated by Django 3.2.7 on 2021-09-26 18:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('playdot', '0004_rename_if_full_row_is_full'),
    ]

    operations = [
        migrations.CreateModel(
            name='GridBoard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('width', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Piece',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='space',
            name='row',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spaces', to='playdot.row'),
        ),
        migrations.CreateModel(
            name='GameData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gid', models.UUIDField()),
                ('metadata', models.JSONField(null=True)),
                ('board', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='game', to='playdot.gridboard')),
                ('next_to_play', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='games_next_in', to='playdot.piece')),
            ],
        ),
        migrations.AlterField(
            model_name='row',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rows', to='playdot.gridboard'),
        ),
        migrations.AlterField(
            model_name='space',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spaces', to='playdot.gridboard'),
        ),
        migrations.DeleteModel(
            name='Board',
        ),
    ]
