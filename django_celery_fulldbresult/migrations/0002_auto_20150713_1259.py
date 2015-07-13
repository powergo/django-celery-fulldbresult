# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_fulldbresult', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskresultmeta',
            name='args',
            field=models.TextField(help_text='JSON encoded positional arguments', default='[]', verbose_name='arguments', blank=True),
        ),
        migrations.AlterField(
            model_name='taskresultmeta',
            name='kwargs',
            field=models.TextField(help_text='JSON encoded keyword arguments', default='{}', verbose_name='keyword arguments', blank=True),
        ),
        migrations.AlterField(
            model_name='taskresultmeta',
            name='status',
            field=models.CharField(default='PENDING', verbose_name='state', max_length=50, choices=[('FAILURE', 'FAILURE'), ('RETRY', 'RETRY'), ('PENDING', 'PENDING'), ('REVOKED', 'REVOKED'), ('RECEIVED', 'RECEIVED'), ('SUCCESS', 'SUCCESS'), ('STARTED', 'STARTED')]),
        ),
    ]
