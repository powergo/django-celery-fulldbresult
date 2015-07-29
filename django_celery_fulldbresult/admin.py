import json

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from celery import current_app

from django_celery_fulldbresult.models import TaskResultMeta


def retry_task(modeladmin, request, queryset):
    """Admin Site Action that retries the selected tasks.
    """
    task_ids = []
    for task in queryset.all():
        task_name = task.task
        task_args = json.loads(task.args)
        task_kwargs = json.loads(task.kwargs)
        result = current_app.send_task(
            task_name, args=task_args, kwargs=task_kwargs)
        task_ids.append(result.task_id)
    modeladmin.message_user(request, "Tasks sent: {0}".format(task_ids))
retry_task.short_description = _("Retry Tasks")


class TaskResultMetaAdmin(admin.ModelAdmin):
    list_display = ("task_id", "task", "date_submitted", "date_done", "status",
                    "eta")
    search_fields = ("task_id", "task")
    list_filter = ("status", )
    actions = [retry_task, ]
    readonly_fields = ("result_repr", )


# Register your models here.
admin.site.register(TaskResultMeta, TaskResultMetaAdmin)
