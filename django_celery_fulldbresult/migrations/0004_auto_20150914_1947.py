# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_celery_fulldbresult.models


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_fulldbresult', '0003_taskresultmeta_eta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskresultmeta',
            name='result',
            field=django_celery_fulldbresult.models.PickledOrJSONObjectField(default=None, null=True, editable=False),
        ),
    ]
