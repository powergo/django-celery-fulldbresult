from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from celery import current_app
from djcelery.admin import PeriodicTaskAdmin
from djcelery.models import PeriodicTask

from django_celery_fulldbresult.models import TaskResultMeta
from django_celery_fulldbresult import serialization


def retry_task(modeladmin, request, queryset):
    """Admin Site Action that retries the selected tasks.
    """
    task_ids = []
    for task in queryset.all():
        task_name = task.task
        task_args = serialization.loads(task.args)
        task_kwargs = serialization.loads(task.kwargs)
        result = current_app.send_task(
            task_name, args=task_args, kwargs=task_kwargs)
        task_ids.append(result.task_id)
    modeladmin.message_user(request, "Tasks sent: {0}".format(task_ids))
retry_task.short_description = _("Retry Tasks")


class TaskResultMetaAdmin(admin.ModelAdmin):
    list_display = ("task_id", "task", "date_submitted", "date_done", "status",
                    "eta")
    search_fields = ("task_id", "task")
    list_filter = ("status", "task")
    actions = [retry_task, ]
    readonly_fields = ("result_repr", )


admin.site.register(TaskResultMeta, TaskResultMetaAdmin)


# Option to override PeriodicTaskAdmin
def trigger_periodic_task(modeladmin, request, queryset):
    """Admin Site Action for django_celery's PeriodicTask that manually
    triggers the selected tasks.
    """
    retry_task(modeladmin, request, queryset)
trigger_periodic_task.short_description = _("Trigger Periodic Tasks")


class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
    actions = [trigger_periodic_task, ]
    list_filter = ("task", )


if getattr(settings, "DJANGO_CELERY_FULLDBRESULT_OVERRIDE_DJCELERY_ADMIN",
           False):
    admin.site.unregister(PeriodicTask)
    admin.site.register(PeriodicTask, CustomPeriodicTaskAdmin)
