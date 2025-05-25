import asyncio
import time

class RateLimiter:
    def __init__(self, max_calls=60, period=60):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = asyncio.Lock()

    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            async with self.lock:
                now = time.time()
                # Remove calls that are outside the period
                self.calls = [call for call in self.calls if call > now - self.period]
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.calls[0] - (now - self.period)
                    await asyncio.sleep(sleep_time)
                self.calls.append(time.time())
            return await func(*args, **kwargs)
        return wrapper
