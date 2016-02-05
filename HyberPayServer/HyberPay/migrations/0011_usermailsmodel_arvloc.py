# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HyberPay', '0010_auto_20160121_2042'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermailsmodel',
            name='ARVLOC',
            field=models.TextField(null=True, blank=True),
        ),
    ]
