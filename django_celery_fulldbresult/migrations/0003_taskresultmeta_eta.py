# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_fulldbresult', '0002_auto_20150713_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskresultmeta',
            name='eta',
            field=models.DateTimeField(verbose_name='eta', null=True, blank=True),
        ),
    ]
