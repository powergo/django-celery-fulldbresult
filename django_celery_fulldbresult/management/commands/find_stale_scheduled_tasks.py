from datetime import timedelta

from django.core.management import BaseCommand

from django_celery_fulldbresult.models import TaskResultMeta


class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            action="store",
            dest="days",
            type=int,
            default=0,
            help="max days before a scheduled task is stale")
        parser.add_argument(
            "--seconds",
            action="store",
            dest="seconds",
            type=int,
            default=0,
            help="max seconds before a task is stale")
        parser.add_argument(
            "--microseconds",
            action="store",
            dest="microseconds",
            type=int,
            default=0,
            help="max microseconds before a task is stale")
        parser.add_argument(
            "--minutes",
            action="store",
            dest="minutes",
            type=int,
            default=0,
            help="max minutes before a task is stale")
        parser.add_argument(
            "--hours",
            action="store",
            dest="hours",
            type=int,
            default=0,
            help="max hours before a task is stale")
        parser.add_argument(
            "--weeks",
            action="store",
            dest="weeks",
            type=int,
            default=0,
            help="max weeks before a task is stale")

    def handle(self, *args, **options):
        delta = timedelta(
            days=options["days"], seconds=options["seconds"],
            microseconds=options["microseconds"], minutes=options["minutes"],
            hours=options["hours"], weeks=options["weeks"])

        tasks = TaskResultMeta.objects.get_stale_scheduled_tasks(
            delta)
        print("Stale scheduled tasks:")
        for task in tasks:
            print("  {0} - {1}: {2}".format(
                task.date_done, task.task_id, task.task))
