from djcelery.managers import TaskManager, transaction_retry


DEFAULT_ARGS = "[]"
DEFAULT_KWARGS = "{}"


class TaskResultManager(TaskManager):

    @transaction_retry(max_retries=2)
    def store_result(
            self, task_id, result, status, traceback=None, children=None,
            task=None, args=DEFAULT_ARGS, kwargs=DEFAULT_KWARGS, expires=None,
            routing_key=None, exchange=None, hostname=None,
            date_submitted=None):
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
