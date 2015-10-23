# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import oauth2client.django_orm


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactsModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='CredentialsModel',
            fields=[
                ('id', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('credential', oauth2client.django_orm.CredentialsField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserContactModel',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('contact_no', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='UserMailsModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orignal_mail', models.TextField()),
                ('user_id', models.ForeignKey(to='HyberPay.UserContactModel')),
            ],
        ),
        migrations.AddField(
            model_name='contactsmodel',
            name='uid',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
