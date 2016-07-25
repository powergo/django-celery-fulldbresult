from celery import current_app
from celery.states import PENDING
from celery.app.task import Context, Task
from celery.signals import before_task_publish
from django_celery_fulldbresult.errors import SchedulingStopPublishing

from django.conf import settings
from django.utils.timezone import now


old_apply_async = Task.apply_async


def new_apply_async(
        self, *args, **kwargs):
    try:
        return old_apply_async(self, *args, **kwargs)
    except SchedulingStopPublishing as exc:
        #
        return self.AsyncResult(exc.task_id)


Task.apply_async = new_apply_async


# TODO MAY NEED ANOTHER OPTION AND ANOTHER RECEIVER IN CASE SOMEONE WANTS TO
# ABOLISH ETA BUT NOT TRACK PUBLISH?
if getattr(settings, "DJANGO_CELERY_FULLDBRESULT_TRACK_PUBLISH", False):
    @before_task_publish.connect
    def update_sent_state(sender=None, body=None, exchange=None,
                          routing_key=None, **kwargs):
        # App may not be loaded on init
        from django_celery_fulldbresult.models import SCHEDULED

        if not getattr(
                settings, "DJANGO_CELERY_FULLDBRESULT_TRACK_PUBLISH", False):
            # Check again to support dynamic change of this settings
            return

        task = current_app.tasks.get(sender)

        if getattr(task, "ignore_result", False) or getattr(
                settings, "CELERY_IGNORE_RESULT", False):
            # Do not save this task result
            return

        backend = task.backend if task else current_app.backend
        request = Context()
        request.update(**body)
        request.date_submitted = now()
        request.delivery_info = {
            "exchange": exchange,
            "routing_key": routing_key
        }

        # TODO More complex check: no chord, no group, etc.
        # print(body)
        if body.get("eta"):
            status = SCHEDULED
        else:
            status = PENDING

        backend.store_result(body["id"], None, status, traceback=None,
                             request=request)

        if status == SCHEDULED:
            raise SchedulingStopPublishing(task_id=body["id"])
