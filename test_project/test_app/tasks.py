from celery import shared_task

from django_celery_fulldbresult.tasks import ScheduledTask


@shared_task
def do_something(param):
    print("DOING SOMETHING")
    return (param, "test")


@shared_task(base=ScheduledTask)
def do_something_alt(param):
    print("DOING SOMETHING")
    return (param, "test")
