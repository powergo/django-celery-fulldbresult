from celery import shared_task


@shared_task
def do_something(param):
    print("DOING SOMETHING")
    return (param, "test")
