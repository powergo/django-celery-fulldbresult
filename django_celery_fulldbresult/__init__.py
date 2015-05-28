from celery import current_app
from celery.states import PENDING
from celery.app.task import Context
from celery.signals import before_task_publish

from django.conf import settings
from django.utils.timezone import now


if getattr(settings, "DJANGO_CELERY_FULLDBRESULT_TRACK_PUBLISH", False):
    @before_task_publish.connect
    def update_sent_state(sender=None, body=None, exchange=None,
                          routing_key=None, **kwargs):
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
        backend.store_result(body["id"], None, PENDING, traceback=None,
                             request=request)
