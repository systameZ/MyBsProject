# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-09-06 01:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='salt_master',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=50, unique=True, verbose_name='主控地址')),
                ('port', models.IntegerField(default=8000, verbose_name='主控端口')),
                ('username', models.CharField(max_length=30, verbose_name='主控用户名')),
                ('password', models.CharField(max_length=30, verbose_name='主控密码')),
                ('link_stat', models.BooleanField(default=False, verbose_name='连接状态')),
            ],
            options={
                'permissions': ('manage_master', '管理主控'),
                'default_permissions': (),
            },
        ),
    ]
