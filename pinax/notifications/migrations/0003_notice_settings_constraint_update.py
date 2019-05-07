# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pinax_notifications', '0002_auto_20171003_2006'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='noticesetting',
            unique_together=("user", "notice_type", "medium")
        ),
    ]
