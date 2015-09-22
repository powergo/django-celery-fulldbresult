django-celery-fulldbresult - Collects information about a task and its result
=============================================================================

:Authors:
  Resulto Developpement Web Inc.
:Version: 0.3.0

This projects has two goals:

1. Provide a result backend that can store enough information about a task to retry it
   if necessary.
2. Provide a way to identify tasks that are never completed (e.g., if the
   worker crashes before it can report the result).

Requirements
------------

django-celery-fulldbresult works with Python 2.7 and 3.4. It requires Celery
3.1+, django-celery 3.1.16+, and Django 1.7+

Installation
------------

::

    pip install django-celery-fulldbresult

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

    import json

    from testcelery.celery import app as celery_app

    from django_celery_fulldbresult.models import TaskResultMeta

    task = TaskResultMeta.objects.all()[0]
    task_name = task.task
    task_args = json.loads(task.args)
    task_kwargs = json.loads(task.kwargs)
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

.. image:: https://raw.githubusercontent.com/resulto-admin/django-celery-fulldbresult/newbackend/admin_screenshot.png


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


License
-------

This software is licensed under the `New BSD License`. See the `LICENSE` file
in the repository for the full license text.
