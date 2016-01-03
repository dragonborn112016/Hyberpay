# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HyberPay', '0006_auto_20151201_1827'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserExpenseModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.CharField(max_length=10)),
                ('month_id', models.IntegerField()),
                ('utility', models.FloatField()),
                ('others', models.FloatField()),
                ('travel', models.FloatField()),
                ('ucm', models.ForeignKey(to='HyberPay.UserContactModel')),
            ],
            options={
                'ordering': ['month_id'],
            },
        ),
        migrations.RemoveField(
            model_name='userdashboardmodel',
            name='ucm',
        ),
        migrations.DeleteModel(
            name='UserDashboardModel',
        ),
    ]
