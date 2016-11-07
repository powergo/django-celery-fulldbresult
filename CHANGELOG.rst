
Changelog - django-celery-fulldbresult
======================================

0.5.2 - November 7th 2016
-------------------------

- Changes default admin options of PeriodicTask.

0.5.1 - October 17th 2016
-------------------------

- Use Kombu (celery) JSON serialization instead of Python serialization.
- No longer automatically monkey patch apply_async: requires a setting and can
  be replaced by using a base task class.

0.5.0 - July 28th 2016
----------------------

- Provide a memory-efficient alternative to a Task's ETA or Countdown.

0.4.1 - November 26th 2015
--------------------------

- Can now filter tasks by name in the PeriodicTask Django Admin.

0.4.0 - November 26th 2015
--------------------------

- Can now filter tasks by name in the Django Admin.

0.3.1 - September 22nd 2015
---------------------------

- Can now force JSON representation even if your task result is not JSON serializable.

0.3.0 - September 22nd 2015
---------------------------

- Task results can be serialized with JSON instead of pickle.
- Task name in result was incorrect when celery reported a failure such as
  hard time limit matched.
- Can override djcelery's PeriodicTaskAdmin to enable manual triggering of
  PeriodicTask items with the Django Admin.

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
