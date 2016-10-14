from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text  # noqa


from celery import states

from djcelery.compat import python_2_unicode_compatible
from djcelery.picklefield import PickledObjectField


from django_celery_fulldbresult import serialization
from django_celery_fulldbresult import managers

SCHEDULED = "SCHEDULED"

SCHEDULED_SENT = "SCHEDULED_SENT"

FULL_RESULTS_ALL_STATES = states.ALL_STATES.union(
    frozenset([SCHEDULED, SCHEDULED_SENT]))


TASK_STATE_CHOICES = sorted(
    zip(FULL_RESULTS_ALL_STATES, FULL_RESULTS_ALL_STATES), key=lambda t: t[0])


def use_json():
    """Returns True if django celery db result is configured to save results as
    JSON.
    """
    return getattr(settings, "DJANGO_CELERY_FULLDBRESULT_USE_JSON", False)


def force_json():
    """Returns True if django celery db result is configured to force JSON even
    if a result is not JSON serializable.
    """
    return getattr(settings, "DJANGO_CELERY_FULLDBRESULT_FORCE_JSON", False)


class PickledOrJSONObjectField(PickledObjectField):
    """Serializes field content using pickle or JSON depending on the
    DJANGO_CELERY_FULLDBRESULT_USE_JSON.
    """

    def get_db_prep_value(self, value, **kwargs):
        if use_json():
            if value is not None:
                try:
                    value = force_text(serialization.dumps(value))
                except TypeError:
                    if force_json():
                        value = force_text(
                            serialization.dumps(
                                {
                                    "value": str(value),
                                    "forced_json": True
                                }
                            )
                        )
                    else:
                        raise
        else:
            value = super(PickledOrJSONObjectField, self).get_db_prep_value(
                value, **kwargs)

        return value

    def to_python(self, value):
        if use_json():
            if value:
                try:
                    value = serialization.loads(value)
                    return value
                except Exception:
                    if isinstance(value, str):
                        # Badly formatted JSON!
                        raise
                    else:
                        return value
            else:
                return None
        else:
            return super(PickledOrJSONObjectField, self).to_python(value)


@python_2_unicode_compatible
class TaskResultMeta(models.Model):
    """Task result/status.
    """

    task_id = models.CharField(_("task id"), max_length=255, unique=True)
    task = models.CharField(_("task name"), max_length=200)
    args = models.TextField(
        _("arguments"), blank=True, default="[]",
        help_text=_("JSON encoded positional arguments"),
    )
    kwargs = models.TextField(
        _("keyword arguments"), blank=True, default="{}",
        help_text=_("JSON encoded keyword arguments"),
    )
    hostname = models.CharField(_('hostname'), max_length=255, blank=True,
                                null=True)
    exchange = models.CharField(
        _('exchange'), max_length=200, blank=True, null=True, default=None,
    )
    routing_key = models.CharField(
        _('routing key'), max_length=200, blank=True, null=True, default=None,
    )
    eta = models.DateTimeField(
        _('eta'), blank=True, null=True,
    )
    expires = models.DateTimeField(
        _('expires'), blank=True, null=True,
    )
    status = models.CharField(
        _("state"),
        max_length=50, default=states.PENDING, choices=TASK_STATE_CHOICES,
    )
    scheduled_id = models.UUIDField(null=True, blank=True)
    result = PickledOrJSONObjectField(null=True, default=None, editable=False)
    date_submitted = models.DateTimeField(
        _("submitted at"), null=True, blank=True)
    date_done = models.DateTimeField(_("done at"), auto_now=True)
    traceback = models.TextField(_("traceback"), blank=True, null=True)
    hidden = models.BooleanField(editable=False, default=False, db_index=True)
    # TODO compression was enabled by mistake in Celery,
    # djcelery recommends to disable it
    # but this is a backwards incompatible change that needs planning.
    meta = PickledObjectField(
        compress=True, null=True, default=None, editable=False,
    )

    objects = managers.TaskResultManager()

    @property
    def result_repr(self):
        return str(self.result)

    class Meta:
        verbose_name = _("task state")
        verbose_name_plural = _("task states")
        db_table = "celery_taskresultmeta"

    def to_dict(self):
        return {"task_id": self.task_id,
                "status": self.status,
                "result": self.result,
                "date_done": self.date_done,
                "traceback": self.traceback,
                "children": (self.meta or {}).get("children")}

    def __str__(self):
        return "<Task: {0.task_id} state={0.status}>".format(self)
