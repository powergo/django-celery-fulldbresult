
Changelog - django-celery-fulldbresult
======================================

0.4.0 - September 18th 2015
---------------------------

- Can override djcelery's PeriodicTaskAdmin to enable manual triggering of
  PeriodicTask items with the Django Admin.

0.3.0 - September 15th 2015
---------------------------

- Task results can be serialized with JSON instead of pickle.
- Task name in result was incorrect when celery reported a failure such as
  hard time limit matched.

0.2.0 - July 30th 2015
----------------------

- Tasks' ETA is now captured in the DB as well and presented in the admin by
  default.

0.1.1 - July 21st 2015
----------------------

- The order of choice fields are now fixed (sorted) so that migrations are not
  re-generated depending on the version of Python or Django.

0.1.0 - June 1st 2015
---------------------

- First release!
- Can store the parameters and enough meta in the task result to retry the task
- Integration with Django Admin: possible to retry a task from a task result
  (admin action)
