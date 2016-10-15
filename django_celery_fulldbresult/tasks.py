from uuid import uuid4

from celery import shared_task, current_app, Task

from django.utils.timezone import now
from django_celery_fulldbresult import serialization
from django_celery_fulldbresult.errors import SchedulingStopPublishing
from django_celery_fulldbresult.models import (
    TaskResultMeta, SCHEDULED, SCHEDULED_SENT)


class ScheduledTask(Task):

    abstract = True

    def apply_async(self, *args, **kwargs):
        try:
            return super(ScheduledTask, self).apply_async(*args, **kwargs)
        except SchedulingStopPublishing as exc:
            # There was an ETA and the task was not sent to the broker.
            # A scheduled task was created instead.
            return self.AsyncResult(exc.task_id)


@shared_task(ignore_result=True)
def send_scheduled_task():
    """Task that sends due scheduled tasks for execution.

    Each DB operation must be in its own commit so that even if
    send_scheduled_task is called multiple times concurrently, a task is
    ensured to only be sent **at most once**. If a crash occurs while sending a
    task, the task will stay indefinitely in the SCHEDULED state while having a
    schedule id.

    1. Tasks due to be executed are marked with a schedule id. This prevents
        the task from being sent for execution twice.

    2. Each task marked by the schedule id is sent for exeuction without an
        ETA.

    3. We change the status from SCHEDULED to SCHEDULED SENT after a task is
        being sent for execution.

    **IMPORTANT: ** Never call this task inside an atomic block or you could
    end up sending tasks more than once. Always use autocommit (each SQL query
    executed in its own transaction).
    """
    limit = now()
    schedule_id = uuid4().hex

    # Mark tasks ready to be scheduled
    TaskResultMeta.objects.filter(
        scheduled_id__isnull=True, eta__lt=limit,
        status=SCHEDULED).update(
        scheduled_id=schedule_id)

    # Fetch and apply by removing eta
    for task in TaskResultMeta.objects.filter(
            scheduled_id=schedule_id).all():
        task_name = task.task
        task_args = serialization.loads(task.args)
        task_kwargs = serialization.loads(task.kwargs)
        result = current_app.send_task(
            task_name, args=task_args, kwargs=task_kwargs)
        task.status = SCHEDULED_SENT
        task.result = {"new_task_id": result.task_id}
        task.save()
