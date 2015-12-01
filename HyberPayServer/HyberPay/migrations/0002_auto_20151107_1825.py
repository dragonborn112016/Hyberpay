# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HyberPay', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailAttachmentModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('fname', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='usermailsmodel',
            name='msgId',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='mailattachmentmodel',
            name='umm',
            field=models.ForeignKey(to='HyberPay.UserMailsModel'),
        ),
    ]
