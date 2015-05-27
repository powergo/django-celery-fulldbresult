from django.contrib import admin

from django_celery_fulldbresult.models import TaskResultMeta


class TaskResultMetaAdmin(admin.ModelAdmin):
    list_display = ("task_id", "task", "date_done", "status")
    search_fields = ("task_id", "task")
    list_filter = ("status", )


# Register your models here.
admin.site.register(TaskResultMeta, TaskResultMetaAdmin)
