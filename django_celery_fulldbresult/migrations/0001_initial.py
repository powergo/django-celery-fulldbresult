# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djcelery.picklefield


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TaskResultMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('task_id', models.CharField(unique=True, verbose_name='task id', max_length=255)),
                ('task', models.CharField(verbose_name='task name', max_length=200)),
                ('args', models.TextField(help_text='JSON encoded positional arguments', verbose_name='Arguments', default='[]', blank=True)),
                ('kwargs', models.TextField(help_text='JSON encoded keyword arguments', verbose_name='Keyword arguments', default='{}', blank=True)),
                ('hostname', models.CharField(verbose_name='hostname', max_length=255, blank=True, null=True)),
                ('exchange', models.CharField(verbose_name='exchange', max_length=200, default=None, blank=True, null=True)),
                ('routing_key', models.CharField(verbose_name='routing key', max_length=200, default=None, blank=True, null=True)),
                ('expires', models.DateTimeField(verbose_name='expires', blank=True, null=True)),
                ('status', models.CharField(verbose_name='state', max_length=50, default='PENDING', choices=[('REVOKED', 'REVOKED'), ('SUCCESS', 'SUCCESS'), ('RECEIVED', 'RECEIVED'), ('PENDING', 'PENDING'), ('RETRY', 'RETRY'), ('FAILURE', 'FAILURE'), ('STARTED', 'STARTED')])),
                ('result', djcelery.picklefield.PickledObjectField(default=None, editable=False, null=True)),
                ('date_submitted', models.DateTimeField(verbose_name='submitted at', blank=True, null=True)),
                ('date_done', models.DateTimeField(verbose_name='done at', auto_now=True)),
                ('traceback', models.TextField(verbose_name='traceback', blank=True, null=True)),
                ('hidden', models.BooleanField(db_index=True, default=False, editable=False)),
                ('meta', djcelery.picklefield.PickledObjectField(default=None, editable=False, null=True)),
            ],
            options={
                'verbose_name_plural': 'task states',
                'verbose_name': 'task state',
                'db_table': 'celery_taskresultmeta',
            },
            bases=(models.Model,),
        ),
    ]
