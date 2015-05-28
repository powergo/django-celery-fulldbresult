from datetime import timedelta
from optparse import make_option

from django.core.management import BaseCommand

from django_celery_fulldbresult.managers import TERMINAL_STATES
from django_celery_fulldbresult.models import TaskResultMeta


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            "--days",
            action="store",
            dest="days",
            type="int",
            default=0,
            help="max days before a task is stale"),
        make_option(
            "--seconds",
            action="store",
            dest="seconds",
            type="int",
            default=0,
            help="max seconds before a task is stale"),
        make_option(
            "--microseconds",
            action="store",
            dest="microseconds",
            type="int",
            default=0,
            help="max microseconds before a task is stale"),
        make_option(
            "--minutes",
            action="store",
            dest="minutes",
            type="int",
            default=0,
            help="max minutes before a task is stale"),
        make_option(
            "--hours",
            action="store",
            dest="hours",
            type="int",
            default=0,
            help="max hours before a task is stale"),
        make_option(
            "--weeks",
            action="store",
            dest="weeks",
            type="int",
            default=0,
            help="max weeks before a task is stale"),
        make_option(
            "--terminal-state",
            action="append",
            dest="terminal_states",
            help="State considered terminal (non-stale). can be repeated."),
    )

    def handle(self, *args, **options):
        delta = timedelta(
            days=options["days"], seconds=options["seconds"],
            microseconds=options["microseconds"], minutes=options["minutes"],
            hours=options["hours"], weeks=options["weeks"])
        acceptable_states = options["terminal_states"]
        if not acceptable_states:
            acceptable_states = TERMINAL_STATES

        tasks = TaskResultMeta.objects.get_stale_tasks(
            delta, acceptable_states).order_by("date_done")
        print("Stale tasks:")
        for task in tasks:
            print("  {0} - {1}: {2}".format(
                task.date_done, task.task_id, task.task))
