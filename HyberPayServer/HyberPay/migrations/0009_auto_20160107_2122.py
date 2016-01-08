# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HyberPay', '0008_auto_20160107_2115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermailsmodel',
            name='timestamp',
            field=models.BigIntegerField(),
        ),
    ]
