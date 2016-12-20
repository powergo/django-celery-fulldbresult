from django.core.management import BaseCommand

from django_celery_fulldbresult import serialization
from django_celery_fulldbresult.models import TaskResultMeta


try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text  # noqa


def str_loads(data, content_type="application/json", encoding="utf-8"):
    """Returns the string instead of trying to convert it.
    """
    return data


class Command(BaseCommand):

    def handle(self, *args, **options):
        real_loads = serialization.loads

        # We monkeypath loads so that query iteration does not fail.
        serialization.loads = str_loads

        query = TaskResultMeta.objects.all()
        count = 0
        fixed = 0

        print("Inspecting {0} task results".format(query.count()))

        for task_result in query:
            count += 1
            result = task_result.result
            if result is None:
                continue
            try:
                real_loads(result)
            except TypeError:
                fixed += 1
                # The result does not correctly load as json.
                new_value = force_text(result)
                # This will call dumps, which will fix badly formatted strings.
                task_result.result = new_value
                task_result.save()

            if count % 1000 == 0:
                print("Inspected {0} task results".format(count))

        if fixed:
            print("Fixed {0} results".format(fixed))
        else:
            print("No result to fix")
