# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-09-09 08:36
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('deploy_more', '0011_auto_20180909_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salt_minion_acc',
            name='minion_acc_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 9, 9, 8, 36, 56, 11566, tzinfo=utc)),
        ),
    ]