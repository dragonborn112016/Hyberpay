# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HyberPay', '0004_mailattachmentmodel_att_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDashboardModel',
            fields=[
                ('ucm', models.OneToOneField(primary_key=True, serialize=False, to='HyberPay.UserContactModel')),
                ('month1', models.CharField(max_length=20)),
                ('month2', models.CharField(max_length=20)),
                ('month3', models.CharField(max_length=20)),
                ('month4', models.CharField(max_length=20)),
                ('month5', models.CharField(max_length=20)),
                ('month6', models.CharField(max_length=20)),
            ],
        ),
    ]
