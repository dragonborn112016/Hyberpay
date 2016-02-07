# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HyberPay', '0011_usermailsmodel_arvloc'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermailsmodel',
            name='Subject',
            field=models.TextField(null=True, blank=True),
        ),
    ]
