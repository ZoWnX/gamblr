# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-25 01:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_auto_20161225_0029'),
    ]

    operations = [
        migrations.RenameField(
            model_name='currency',
            old_name='short_name',
            new_name='code',
        ),
    ]