# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HyberPay', '0005_userdashboardmodel'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usermailsmodel',
            options={'ordering': ['-timestamp']},
        ),
    ]
