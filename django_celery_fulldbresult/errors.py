from __future__ import absolute_import, unicode_literals


class SchedulingStopPublishing(Exception):
    """Raised before publishing a scheduled task to prevent Celery from sending
    the task to the broker.
    """
    def __init__(self, task_id):
        super(SchedulingStopPublishing, self).__init__()
        self.task_id = task_id
