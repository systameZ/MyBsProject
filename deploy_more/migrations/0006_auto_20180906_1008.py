# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-09-06 02:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deploy_more', '0005_auto_20180906_1006'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salt_master',
            options={'permissions': ('manage_master', '管理主控')},
        ),
    ]