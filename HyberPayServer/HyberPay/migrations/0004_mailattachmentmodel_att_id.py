# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HyberPay', '0003_remove_mailattachmentmodel_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailattachmentmodel',
            name='att_id',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
    ]
