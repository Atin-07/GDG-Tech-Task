"""Global rate limiter shared by all worker threads."""
import random
import threading
import time


class RateLimiter:
    """Spaces out request START times so total request rate never exceeds the configured delay,
    no matter how many workers are running."""

    def __init__(self, min_interval, jitter):
        self.min_interval = min_interval
        self.jitter = jitter
        self._lock = threading.Lock()
        self._next_slot = 0.0

    def wait(self):
        with self._lock:
            now = time.monotonic()
            slot = max(now, self._next_slot)
            self._next_slot = slot + self.min_interval + random.uniform(0, self.jitter)
        delay = slot - now
        if delay > 0:
            time.sleep(delay)
