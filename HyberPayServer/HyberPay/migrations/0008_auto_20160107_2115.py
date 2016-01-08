# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HyberPay', '0007_auto_20151214_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercontactmodel',
            name='mailJson',
            field=models.TextField(default='[]'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usermailsmodel',
            name='DD',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usermailsmodel',
            name='DEPLOC',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usermailsmodel',
            name='DOD',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usermailsmodel',
            name='ITEM',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usermailsmodel',
            name='PURP',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usermailsmodel',
            name='TOD',
            field=models.TextField(null=True, blank=True),
        ),
    ]
