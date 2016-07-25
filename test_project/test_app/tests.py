from datetime import timedelta, datetime, tzinfo
import json
from time import sleep

from celery.states import PENDING

from django.core.management import call_command
from django.test import TransactionTestCase

from django_celery_fulldbresult.models import TaskResultMeta, SCHEDULED

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
        task = TaskResultMeta.objects.all()[0]
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

    def test_parameters_schedule_eta(self):
        with self.settings(DJANGO_CELERY_FULLDBRESULT_SCHEDULE_ETA=True):
            a_date = datetime(2080, 1, 1, tzinfo=utc)
            do_something.apply_async(
                kwargs={"param": "testing"}, eta=a_date)
            task = TaskResultMeta.objects.all()[0]
            self.assertEqual(
                "test_app.tasks.do_something",
                task.task)

            # This is new and was never set in previous backend. It is only set
            # before the task is published.
            self.assertIsNotNone(task.date_submitted)

            # Task is never executed because eager = false
            self.assertEqual(SCHEDULED, task.status)

            # Attributes such as eta are preserved
            self.assertEqual(a_date, task.eta)

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
        sleep(0.1)
        call_command("find_stale_tasks", microseconds=1)
