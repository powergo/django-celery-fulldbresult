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
            field=models.TextField(help_text='JSON encoded positional arguments', blank=True, verbose_name='arguments', default='[]'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='taskresultmeta',
            name='kwargs',
            field=models.TextField(help_text='JSON encoded keyword arguments', blank=True, verbose_name='keyword arguments', default='{}'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='taskresultmeta',
            name='status',
            field=models.CharField(choices=[('FAILURE', 'FAILURE'), ('PENDING', 'PENDING'), ('RECEIVED', 'RECEIVED'), ('RETRY', 'RETRY'), ('REVOKED', 'REVOKED'), ('STARTED', 'STARTED'), ('SUCCESS', 'SUCCESS')], verbose_name='state', default='PENDING', max_length=50),
            preserve_default=True,
        ),
    ]
