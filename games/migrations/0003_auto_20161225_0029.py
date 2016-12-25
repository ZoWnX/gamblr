# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-25 00:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_auto_20161214_0121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('symbol', models.CharField(max_length=5)),
                ('short_name', models.CharField(max_length=3)),
            ],
            options={
                'verbose_name_plural': 'currencies',
            },
        ),
        migrations.AddField(
            model_name='game',
            name='currency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='games.Currency'),
        ),
    ]