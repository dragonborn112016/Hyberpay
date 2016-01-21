# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HyberPay', '0009_auto_20160107_2122'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usermailsmodel',
            unique_together=set([('msgId', 'ucm')]),
        ),
    ]
