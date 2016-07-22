from datetime import timedelta, datetime, tzinfo
import json
from uuid import uuid4

from celery.states import PENDING

from django.core.management import call_command
from django.test import TransactionTestCase

from django_celery_fulldbresult.models import (
    TaskResultMeta, SCHEDULED, SCHEDULED_SENT)
from django_celery_fulldbresult.tasks import send_scheduled_task

from test_app.tasks import do_something

# Create your tests here.

ZERO = timedelta(0)


class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

utc = UTC()


class SignalTest(TransactionTestCase):

    def test_parameters(self):
        a_date = datetime(2080, 1, 1, tzinfo=utc)
        do_something.apply_async(
            kwargs={"param": "testing"}, eta=a_date)
        task = TaskResultMeta.objects.order_by("pk")[0]
        self.assertEqual(
            "test_app.tasks.do_something",
            task.task)

        # This is new and was never set in previous backend. It is only set
        # before the task is published.
        self.assertIsNotNone(task.date_submitted)

        # Task is never executed because eager = false
        self.assertEqual(PENDING, task.status)

        # Attributes such as eta are preserved
        self.assertEqual(a_date, task.eta)

        kwargs = json.loads(task.kwargs)
        self.assertEqual(kwargs, {"param": "testing"})

    def test_parameters_ignore_result(self):
        with self.settings(CELERY_IGNORE_RESULT=True):
            a_date = datetime(2080, 1, 1, tzinfo=utc)
            do_something.apply_async(
                kwargs={"param": "testing"}, eta=a_date)
            self.assertEqual(0, TaskResultMeta.objects.count())

    def test_parameters_schedule_eta(self):
        with self.settings(DJANGO_CELERY_FULLDBRESULT_SCHEDULE_ETA=True):
            a_date = datetime(2080, 1, 1, tzinfo=utc)
            do_something.apply_async(
                kwargs={"param": "testing"}, eta=a_date)
            task = TaskResultMeta.objects.order_by("pk")[0]
            self.assertEqual(
                "test_app.tasks.do_something",
                task.task)

            # This is new and was never set in previous backend. It is only set
            # before the task is published.
            self.assertIsNotNone(task.date_submitted)

            self.assertEqual(SCHEDULED, task.status)

            # Attributes such as eta are preserved
            self.assertEqual(a_date, task.eta)

            kwargs = json.loads(task.kwargs)
            self.assertEqual(kwargs, {"param": "testing"})

    def test_parameters_schedule_eta_ignore_result(self):
        with self.settings(DJANGO_CELERY_FULLDBRESULT_SCHEDULE_ETA=True,
                           CELERY_IGNORE_RESULT=True):
            a_date = datetime(2080, 1, 1, tzinfo=utc)
            do_something.apply_async(
                kwargs={"param": "testing"}, eta=a_date)
            task = TaskResultMeta.objects.order_by("pk")[0]
            self.assertEqual(
                "test_app.tasks.do_something",
                task.task)

            # This is new and was never set in previous backend. It is only set
            # before the task is published.
            self.assertIsNotNone(task.date_submitted)

            self.assertEqual(SCHEDULED, task.status)

            # Attributes such as eta are preserved
            self.assertEqual(a_date, task.eta)

            kwargs = json.loads(task.kwargs)
            self.assertEqual(kwargs, {"param": "testing"})


class SchedulingTest(TransactionTestCase):

    def test_parameters_schedule_eta(self):
        with self.settings(DJANGO_CELERY_FULLDBRESULT_SCHEDULE_ETA=True):
            a_date = datetime(1990, 1, 1, tzinfo=utc)
            do_something.apply_async(
                kwargs={"param": "testing"}, eta=a_date)
            task = TaskResultMeta.objects.order_by("pk")[0]
            self.assertEqual(
                "test_app.tasks.do_something",
                task.task)
            self.assertEqual(SCHEDULED, task.status)

            send_scheduled_task()

            task = TaskResultMeta.objects.order_by("pk")[0]
            new_task = TaskResultMeta.objects.order_by("pk")[1]

            # Old task has been marked as sent
            self.assertEqual(SCHEDULED_SENT, task.status)

            # Old task has a scheduling id
            self.assertIsNotNone(task.scheduled_id)

            # New task is pending (sent for execution)
            self.assertEqual(PENDING, new_task.status)

            # No ETA on the new task
            self.assertIsNone(new_task.eta)

            # The task is of the new task is in the result of the scheduled
            # task for traceability.
            self.assertEqual(task.result["new_task_id"], new_task.task_id)


class ManagerTest(TransactionTestCase):

    def test_get_stale_tasks(self):
        do_something.delay(param="testing")
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

    def test_get_stale_scheduled_tasks(self):
        with self.settings(DJANGO_CELERY_FULLDBRESULT_SCHEDULE_ETA=True):
            a_date = datetime(1990, 1, 1, tzinfo=utc)
            do_something.apply_async(
                kwargs={"param": "testing"}, eta=a_date)
            task = TaskResultMeta.objects.order_by("pk")[0]
            # Mock bad execution
            task.scheduled_id = uuid4().hex
            task.save()

            self.assertEqual(
                1, len(TaskResultMeta.objects.get_stale_scheduled_tasks()))

            self.assertEqual(
                0,
                len(TaskResultMeta.objects.get_stale_scheduled_tasks(
                    timedelta(days=365*100))))


class ResultTest(TransactionTestCase):

    def test_param_result(self):
        a_date = datetime(2080, 1, 1, tzinfo=utc)

        do_something.apply_async(
            kwargs={"param": "testing"}, eta=a_date)
        task = TaskResultMeta.objects.all()[0]
        # Fake result with objects that are not serializable by json but that
        # are serializable by pickle.
        result = ("testing", "test", a_date)
        task.result = result
        task.save()

        # Test pickling/unpickling
        task = TaskResultMeta.objects.all()[0]
        self.assertEqual(task.result, result)

    def test_param_result_as_json(self):
        a_date = datetime(2080, 1, 1, tzinfo=utc)

        with self.settings(DJANGO_CELERY_FULLDBRESULT_USE_JSON=True):
            do_something.apply_async(
                kwargs={"param": "testing"}, eta=a_date)
            task = TaskResultMeta.objects.all()[0]
            # Fake result
            result = ["testing", "test"]
            task.result = result
            task.save()

            # Test pickling/unpickling
            task = TaskResultMeta.objects.all()[0]
            self.assertEqual(task.result, result)

    def test_param_result_as_json_unserializable(self):
        a_date = datetime(2080, 1, 1, tzinfo=utc)

        with self.settings(DJANGO_CELERY_FULLDBRESULT_USE_JSON=True):
            do_something.apply_async(
                kwargs={"param": "testing"}, eta=a_date)
            task = TaskResultMeta.objects.all()[0]

            with self.assertRaises(TypeError):
                # Fake result
                result = ["testing", "test", a_date]
                task.result = result
                task.save()

    def test_param_result_as_json_unserializable_but_force(self):
        a_date = datetime(2080, 1, 1, tzinfo=utc)

        with self.settings(
                DJANGO_CELERY_FULLDBRESULT_USE_JSON=True,
                DJANGO_CELERY_FULLDBRESULT_FORCE_JSON=True):
            do_something.apply_async(
                kwargs={"param": "testing"}, eta=a_date)
            task = TaskResultMeta.objects.all()[0]

            result = ["testing", "test", a_date]
            task.result = result
            task.save()

            # Test pickling/unpickling
            task = TaskResultMeta.objects.all()[0]
            self.assertEqual(
                task.result,
                {"value": str(result), "forced_json": True})


class CommandTest(TransactionTestCase):

    def test_find_stale_tasks_command(self):
        # Just make sure that there is no exception
        do_something.delay(param="testing")
        call_command("find_stale_tasks", microseconds=1)

    def test_find_stale_scheduled_tasks_command(self):
        # Just make sure that there is no exception
        a_date = datetime(1990, 1, 1, tzinfo=utc)
        do_something.apply_async(
            kwargs={"param": "testing"}, eta=a_date)
        call_command("find_stale_scheduled_tasks", microseconds=1)
