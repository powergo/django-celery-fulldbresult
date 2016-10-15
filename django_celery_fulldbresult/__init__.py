from __future__ import absolute_import, unicode_literals

from celery import current_app
from celery.states import PENDING
from celery.app.task import Context, Task
from celery.signals import before_task_publish
from django_celery_fulldbresult.errors import SchedulingStopPublishing

from django.conf import settings
from django.utils.timezone import now


schedule_eta = getattr(
    settings, "DJANGO_CELERY_FULLDBRESULT_SCHEDULE_ETA", False)

track_publish = getattr(
    settings, "DJANGO_CELERY_FULLDBRESULT_TRACK_PUBLISH", False)

monkey_patch_async = getattr(
    settings, "DJANGO_CELERY_FULLDBRESULT_MONKEY_PATCH_ASYNC", False)

old_apply_async = Task.apply_async


def new_apply_async(self, *args, **kwargs):
    try:
        return old_apply_async(self, *args, **kwargs)
    except SchedulingStopPublishing as exc:
        # There was an ETA and the task was not sent to the broker.
        # A scheduled task was created instead.
        return self.AsyncResult(exc.task_id)


def apply_async_monkey_patch():
    Task.apply_async = new_apply_async


def unapply_async_monkey_patch():
    Task.apply_async = old_apply_async


if monkey_patch_async:
    apply_async_monkey_patch()


if track_publish or schedule_eta:
    @before_task_publish.connect
    def update_sent_state(sender=None, body=None, exchange=None,
                          routing_key=None, **kwargs):
        # App may not be loaded on init
        from django_celery_fulldbresult.models import SCHEDULED

        task = current_app.tasks.get(sender)
        save = False
        status = None

        schedule_eta = getattr(
            settings, "DJANGO_CELERY_FULLDBRESULT_SCHEDULE_ETA", False)

        track_publish = getattr(
            settings, "DJANGO_CELERY_FULLDBRESULT_TRACK_PUBLISH", False)

        ignore_result = getattr(task, "ignore_result", False) or\
            getattr(settings, "CELERY_IGNORE_RESULT", False)

        if schedule_eta and body.get("eta") and not body.get("chord")\
                and not body.get("taskset"):
            status = SCHEDULED
            save = True
        elif track_publish and not ignore_result:
            status = PENDING
            save = True

        if save:
            backend = task.backend if task else current_app.backend
            request = Context()
            request.update(**body)
            request.date_submitted = now()
            request.delivery_info = {
                "exchange": exchange,
                "routing_key": routing_key
            }
            backend.store_result(
                body["id"], None, status, traceback=None, request=request)

        if status == SCHEDULED:
            raise SchedulingStopPublishing(task_id=body["id"])
