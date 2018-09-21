from django.db import models
from django.utils.translation import ugettext_lazy as _
import django.utils.timezone as timezone


# Create your models here.

class salt_master(models.Model):
    master_host = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        verbose_name=u'主控地址'
    )
    master_port = models.CharField(max_length=15, default=8000, verbose_name=u'主控端口')
    master_user = models.CharField(max_length=30, null=True, verbose_name=u'主控用户名')
    master_pwd = models.CharField(max_length=30, null=True, verbose_name=u'主控密码')
    master_link_stat = models.BooleanField(default=False, verbose_name=u'连接状态')

    def __str__(self):
        return self.master_host

    class Meta:
        default_permissions = ()
        permissions = (
            ('manage_master', _(u'管理主控')),
            ('list_master', _(u'查看主控')),
        )


class salt_minion_acc(models.Model):
    minion_acc_host = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        verbose_name=u'已授权从机地址'
    )
    minion_acc_master = models.CharField(
        max_length=50,
        null=True,
        verbose_name=u'所属主控'
    )
    minion_acc_stat = models.BooleanField(default=False, verbose_name=u'已授权从机状态')
    minion_acc_time=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.minion_acc_host

    class Meta:
        default_permissions = ()
        permissions = (
            ('manage_minion', _(u'管理从机')),
            ('list_minion', _(u'查看从机')),
        )


class salt_minion_una(models.Model):
    minion_una_host = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        verbose_name=u'未授权从机地址'
    )
    minion_una_master = models.ForeignKey(salt_master,to_field='master_host',on_delete=models.CASCADE)
    minion_una_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.minion_una_host

    class Meta:
        default_permissions = ()
        permissions = (
            ('manage_minion', _(u'管理从机')),
            ('list_minion', _(u'查看从机')),
        )
