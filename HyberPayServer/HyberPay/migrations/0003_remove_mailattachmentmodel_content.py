# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HyberPay', '0002_auto_20151107_1825'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mailattachmentmodel',
            name='content',
        ),
    ]
