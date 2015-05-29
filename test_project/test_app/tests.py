from datetime import timedelta
import json
from time import sleep

from celery.states import PENDING

from django.core.management import call_command
from django.test import TransactionTestCase

from django_celery_fulldbresult.models import TaskResultMeta

from test_app.tasks import do_something

# Create your tests here.


class SignalTest(TransactionTestCase):

    def test_parameters(self):
        do_something.delay(param="testing")
        task = TaskResultMeta.objects.all()[0]
        self.assertEqual(
            "test_app.tasks.do_something",
            task.task)

        # This is new and was never set in previous backend. It is only set
        # before the task is published.
        self.assertIsNotNone(task.date_submitted)

        # Task is never executed because eager = false
        self.assertEqual(PENDING, task.status)

        kwargs = json.loads(task.kwargs)
        self.assertEqual(kwargs, {"param": "testing"})


class ManagerTest(TransactionTestCase):

    def test_get_stale_tasks(self):
        do_something.delay(param="testing")
        sleep(0.1)
        # The task we created is PENDING, so stale
        self.assertEqual(
            1, len(TaskResultMeta.objects.get_stale_tasks()))

        # The task we created still has one hour to go before becoming stale.
        self.assertEqual(
            0, len(TaskResultMeta.objects.get_stale_tasks(timedelta(hours=1))))

        # PENDING is an acceptable state (not stale)
        self.assertEqual(
            0,
            len(TaskResultMeta.objects.get_stale_tasks(
                acceptable_states=[PENDING])))


class CommandTest(TransactionTestCase):

    def test_find_stale_tasks_command(self):
        # Just make sure that there is no exception
        do_something.delay(param="testing")
        sleep(0.1)
        call_command("find_stale_tasks", microseconds=1)
