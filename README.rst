django-celery-fulldbresult - Collects information about a task and its result
=============================================================================

:Authors:
  Resulto Developpement Web Inc.
:Version: 0.5.1

This project adds many small features about the regular Django DB result
backend. django-celery-fulldbresult provides three main features:

1. A result backend that can store enough information about a task to retry it
   if necessary;
2. A memory-efficient alternative to a task's ETA or countdown;
3. Django commands to identify tasks that are never completed or that are
   scheduled but never sent (e.g., if the worker crashes before it can report
   the result or while a scheduled task is being sent to a worker).

Requirements
------------

django-celery-fulldbresult works with Python 2.7 and 3.4+. It requires Celery
3.1+, django-celery 3.1.16+, and Django 1.7+

Installation
------------

Install the library
~~~~~~~~~~~~~~~~~~~

::

    pip install django-celery-fulldbresult


Add the library to your INSTALLED_APPS in your Django Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'djcelery',
        'django_celery_fulldbresult',
    )


Set the following minimal settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Required, won't work if set to True
    CELERY_ALWAYS_EAGER = False

    CELERY_IGNORE_RESULT = False

    CELERY_RESULT_BACKEND =\
        'django_celery_fulldbresult.result_backends:DatabaseResultBackend'

    DJANGO_CELERY_FULLDBRESULT_TRACK_PUBLISH = True

    DJANGO_CELERY_FULLDBRESULT_OVERRIDE_DJCELERY_ADMIN = True


If you use a custom AdminSite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    from djcelery.models import PeriodicTask
    from django_celery_fulldbresult.admin import (
        TaskResultMetaAdmin, CustomPeriodicTaskAdmin)
    from django_celery_fulldbresult.models import TaskResultMeta


    class MySite(AdminSite):
        pass


    site = MySite()
    site.register(TaskResultMeta, TaskResultMetaAdmin)
    site.register(PeriodicTask, CustomPeriodicTaskAdmin)

Note: if you do not use a custom admin site, the admin sections will be
automatically registered and you have nothing to do.


Usage
-----

As a result backend
~~~~~~~~~~~~~~~~~~~

Just set these variables in your settings.py file:

::

    CELERY_RESULT_BACKEND = 'django_celery_fulldbresult.result_backends:DatabaseResultBackend'
    CELERY_IGNORE_RESULT = False


Tasks can be retrieved with the ``TaskResultMeta`` model:

::

    from testcelery.celery import app as celery_app

    from django_celery_fulldbresult.models import TaskResultMeta
    from django_celery_fulldbresult import serialization

    task = TaskResultMeta.objects.all()[0]
    task_name = task.task
    task_args = serialization.loads(task.args)
    task_kwargs = serialization.loads(task.kwargs)
    celery_app.send_task(task_name, args=task_args, kwargs=task_kwargs)


As a way to detect tasks that never complete
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, set this variable in your settings.py file:

::

    DJANGO_CELERY_FULLDBRESULT_TRACK_PUBLISH = True

This will save the task in the database with a status of PENDING.


If you want to get all tasks that are more than one-hour old and are still
pending:

::

    from datetime import timedelta
    from django_celery_fulldbresult.models import TaskResultMeta

    # Returns a QuerySet
    stale_tasks = TaskResultMeta.objects.get_stale_tasks(timedelta(hours=1))


You can also use the ``find_stale_tasks`` Django command:

::

    $ python manage.py find_stale_tasks --hours 1
    Stale tasks:
      2015-05-27 14:17:37.096366+00:00 - cf738350-afe8-44f8-9eac-34721581eb61: email_workers.tasks.send_email

Finally, the task results are automatically added to the Django Admin site. You
can select task results and retry them: this action will send a copy of each
task to the worker using the routes you have defined.

.. image:: https://raw.githubusercontent.com/resulto-admin/django-celery-fulldbresult/master/admin_screenshot.png


With JSON storage
~~~~~~~~~~~~~~~~~

Set this variable in your settings.py file:

::

    DJANGO_CELERY_FULLDBRESULT_USE_JSON = True

This will make sure that results are saved in JSON-compatible string in the
database. With a database such as PostgreSQL, you can apply JSON operators on
the result column. You can also apply any text-based operators in the extra
clause of a Django queryset.

If you use this setting, make sure that the result returned by your task is
JSON-serializable.

If some results are not JSON-serializable, you can store their string
representation by setting this variable in your settings.py file:

::

    DJANGO_CELERY_FULLDBRESULT_FORCE_JSON = True

This will save the following structure:

::

    {
        "value": str(task_result),
        "forced_json": True
    }



Manual trigger of PeriodicTask items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set this variable in your settings.py file:

::

    DJANGO_CELERY_FULLDBRESULT_OVERRIDE_DJCELERY_ADMIN = True

This will override small parts of the django-celery Admin to enable the
manual launch of PeriodicTask items.


Alternative Celery Scheduling (ETA and Countdown)
-------------------------------------------------

Although Celery allows users to schedule the execution of a task by specifying
an ETA or a countdown, the implementation has at least one main limitation with
respect to memory consumption: `all workers try to load all tasks with an ETA,
potentially leading to a large memory consumption
<https://github.com/celery/celery/issues/2218>`_.

django-celery-fulldbresult proposes an alternative to regular celery ETA with slightly different
semantics:

1. When a task is sent with an ETA or a countdown, django-celery-fulldbresult
   intercepts the task and saves it with a status of `SCHEDULED`.

2. A periodic task checks at a configured interval whether the ETA of a task
   has expired.

3. Once a task is due, a new task with the same parameters but without an ETA
   is submitted.

4. The task id of the new task is saved in the result of the original scheduled
   task and the state of the original scheduled task is set to
   `SCHEDULED_SENT`.

Configuration
~~~~~~~~~~~~~

Set this variable in your settings.py file:

::

    DJANGO_CELERY_FULLDBRESULT_SCHEDULE_ETA = True

    # If you do not want to change your code, set this variable too:
    DJANGO_CELERY_FULLDBRESULT_MONKEY_PATCH_ASYNC = True

Then create a periodic task in the Django admin or within your code. For
example:

- Set the cron to ``*/1`` minute, ``*`` for everything else.
- The task is "django_celery_fulldbresult.tasks.send_scheduled_task"
- No other parameters

That's it. When you call a task with an ETA, django-celery-fulldbresult will
automatically intercept the task. For example:


::

    my_task.apply_async(args=[...], kwargs={...}, eta=some_date)


Using a Base Task
~~~~~~~~~~~~~~~~~

When ``DJANGO_CELERY_FULLDBRESULT_MONKEY_PATCH_ASYNC`` is set to True, the
Task.apply_async is monkey patched to correctly handle scheduled tasks.

This will usually work if you correctly use the ``@shared_task`` or
``@app.task`` decorators. It will probably fail if you use the legacy ``@task``
decorator though.

If you encounter any problem with the monkey patching, simply set
``DJANGO_CELERY_FULLDBRESULT_MONKEY_PATCH_ASYNC`` to False and instead, use a
base task:


::

    from celery import shared_task
    from django_celery_fulldbresult.tasks import ScheduledTask

    @shared_task(base=ScheduledTask)
    def do_something(param):
        print("DOING SOMETHING")
        return (param, "test")


Semantics
~~~~~~~~~

The task is guaranteed to:

1. Be sent at most once.
2. Be sent after the ETA has expired (i.e., not before)

If a crash occurs before a task is fully sent, the state of the scheduled task
will be `SCHEDULED` and the task will have a non-null UUID `scheduled id`. We
call these "stale scheduled tasks". It is the user responsibility to manually
resubmit stale scheduled tasks once the application recovers from the crash.


Identifying stale scheduled tasks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the get_stale_scheduled_tasks manager to find stale scheduled
tasks.

::

    from datetime import timedelta
    from django_celery_fulldbresult.models import TaskResultMeta

    # Returns a QuerySet
    stale_tasks = TaskResultMeta.objects.get_stale_scheduled_tasks(timedelta(hours=1))


You can also use the ``find_stale_scheduled_tasks`` Django command:

::

    $ python manage.py find_stale_tasks --hours 1
    Stale scheduled tasks:
      2015-05-27 14:17:37.096366+00:00 - cf738350-afe8-44f8-9eac-34721581eb61: email_workers.tasks.send_email


License
-------

This software is licensed under the `New BSD License`. See the `LICENSE` file
in the repository for the full license text.


Signing GPG Key
---------------

The following GPG keys can be used to sign tags and release files:

- Resulto Development Team: AEC378AB578FF0FC
- Barthelemy Dagenais: 76320A1B901510C4
