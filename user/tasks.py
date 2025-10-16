import time
from django.conf import settings
from datetime import datetime
from service_core.celery import app
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class LockTask(app.Task):
    """
    This abstract class ensures the same tasks run only once at a time.
    """
    abstract = True
    TTL = getattr(settings, 'DEFAULT_TASK_LOCK_TTL', 60 * 6)

    def __init__(self, *args, **kwargs):
        super(LockTask, self).__init__(*args, **kwargs)

    def generate_lock_cache_key(self, *args, **kwargs):
        """
        Simple cache key generator.
        Returns a single key by stringifying the task name and all args and kwargs.
        """
        args_key = [str(arg) for arg in args]
        kwargs_key = [f"{k}={v}" for k, v in sorted(kwargs.items())]
        return "_".join([self.name] + args_key + kwargs_key)

    def __call__(self, *args, **kwargs):
        """check task"""
        lock_cache_key = (self.request.headers or {}).pop('cache_key', None)
        if not lock_cache_key:
            lock_cache_key = self.generate_lock_cache_key(*args, **kwargs)

        print(f'Task {lock_cache_key} is running..')

        lock_time = datetime.now().isoformat()
        lock_acquired = cache.set(lock_cache_key, lock_time, nx=True, timeout=self.TTL)

        if lock_acquired:
            try:
                return self.run(*args, **kwargs)
            finally:
                cache.delete(lock_cache_key)
        else:
            print('Task %s is already running..' % lock_cache_key)

        print(f'Task {lock_cache_key} is finished..')


@app.task(bind=True, base=LockTask)
def test_lock_task(self, user_id):
    """
    For testing the LockTask functionality.
    """
    print(f"Running for {user_id}")
    time.sleep(10)
    return f"Completed for {user_id}"

