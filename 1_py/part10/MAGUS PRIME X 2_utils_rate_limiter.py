import threading
import time


class RateLimiter:
    """
    A thread-safe rate limiter that ensures a minimum interval between API calls.
    """

    def __init__(self, interval: float):
        """
        Initialize the RateLimiter.
        :param interval: Minimum time (in seconds) between allowed calls.
        """
        self.interval = interval
        self._last_call = 0.0
        self._lock = threading.Lock()

    def wait(self):
        """
        Wait until enough time has passed since the last call.
        This method blocks if necessary to enforce the rate limit.
        """
        with self._lock:
            current_time = time.time()
            elapsed = current_time - self._last_call
            if elapsed < self.interval:
                time.sleep(self.interval - elapsed)
            self._last_call = time.time()


# Example usage:
# rate_limiter = RateLimiter(0.5)
# rate_limiter.wait()  # Call before API requests
