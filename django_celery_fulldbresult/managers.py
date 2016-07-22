from __future__ import absolute_import, unicode_literals

from celery.states import SUCCESS, FAILURE
from djcelery.managers import TaskManager, transaction_retry

from django.utils.timezone import now


DEFAULT_ARGS = "[]"
DEFAULT_KWARGS = "{}"
TERMINAL_STATES = (
    SUCCESS,
    FAILURE
)


class TaskResultManager(TaskManager):

    def get_stale_scheduled_tasks(self, max_duration=None):
        """Selects scheduled tasks, which are stale: they have an old ETA, they
        have a scheduled state and a scheduled id, but probably were never sent
        for execution.
        """
        from django_celery_fulldbresult.models import SCHEDULED

        max_date = now()
        if max_duration:
            max_date = now() - max_duration

        return self.filter(
            eta__lte=max_date, status=SCHEDULED,
            scheduled_id__isnull=False)

    def get_stale_tasks(self, max_duration=None, acceptable_states=None):
        """Selects tasks, which are stale: they were last updated before
        now-max_duration and they are not in one of the acceptable_states.

        :keyword max_duration: A timedelta. If None, the timedelta is 0.
        :keyword acceptable_states: A collection of states that are considered
            terminal. Tasks that are not in an acceptable state are
            considered stale. Default to (SUCCESS, FAILURE)
        :rtype: QuerySet
        """
        max_date = now()
        if max_duration:
            max_date = now() - max_duration

        if not acceptable_states:
            acceptable_states = TERMINAL_STATES

        return self.filter(date_done__lte=max_date).exclude(
            status__in=acceptable_states)

    @transaction_retry(max_retries=2)
    def store_result(
            self, task_id, result, status, traceback=None, children=None,
            task=None, args=DEFAULT_ARGS, kwargs=DEFAULT_KWARGS, expires=None,
            routing_key=None, exchange=None, hostname=None,
            date_submitted=None, eta=None):
        """Store the result and status of a task.
        :param task_id: task id
        :param result: The return value of the task, or an exception
            instance raised by the task.
        :param status: Task status. See
            :meth:`celery.result.AsyncResult.get_status` for a list of
            possible status values.
        :keyword traceback: The traceback at the point of exception (if the
            task failed).
        :keyword children: List of serialized results of subtasks
            of this task.
        :keyword exception_retry_count: How many times to retry by
            transaction rollback on exception. This could theoretically
            happen in a race condition if another worker is trying to
            create the same task. The default is to retry twice.
        :keyword task: todo
        :keyword args: todo
        :keyword kwargs: todo
        :keyword expires: todo
        :keyword routing_key: todo
        :keyword exchange: todo
        :keyword hostname: todo
        :keyword date_submitted: todo
        :keyword eta: todo
        """
        defaults = {
            "status": status,
            "result": result,
            "traceback": traceback,
            "task": task,
            "args": args,
            "kwargs": kwargs,
            "expires": expires,
            "routing_key": routing_key,
            "exchange": exchange,
            "hostname": hostname,
            "eta": eta,
            "meta": {
                "children": children
            }
        }

        if date_submitted is not None:
            # Only set date_submitted if not None
            defaults["date_submitted"] = date_submitted

        return self.update_or_create(
            task_id=task_id,
            defaults=defaults
        )
