"""Thread module emulating a subset of Java's threading model."""

import _thread
import logging
import threading
import time
from _weakrefset import WeakSet
from collections import deque as _deque
from itertools import count as _count
from time import monotonic as _time
from typing import Any, Callable, Dict, List, Optional, Tuple

__all__ = [
    "get_ident",
    "active_count",
    "Condition",
    "current_thread",
    "enumerate",
    "main_thread",
    "TIMEOUT_MAX",
    "Event",
    "Lock",
    "RLock",
    "Semaphore",
    "BoundedSemaphore",
    "Thread",
    "Barrier",
    "BrokenBarrierError",
    "Timer",
    "ThreadError",
    "setprofile",
    "settrace",
    "local",
    "stack_size",
    "excepthook",
    "ExceptHookArgs",
    "gettrace",
    "getprofile",
]

_allocate_lock = _thread.allocate_lock
get_ident = _thread.get_ident
try:
    get_native_id = _thread.get_native_id
    _HAVE_THREAD_NATIVE_ID = True
except AttributeError:
    _HAVE_THREAD_NATIVE_ID = False
ThreadError = _thread.error
try:
    _CRLock = _thread.RLock
except AttributeError:
    _CRLock = None
TIMEOUT_MAX = _thread.TIMEOUT_MAX
del _thread

# Support for profile and trace hooks

_profile_hook = None
_trace_hook = None


def setprofile(func):
    """Set a profile function for all threads started from the threading module."""
    global _profile_hook
    _profile_hook = func


def getprofile():
    """Get the profiler function as set by threading.setprofile()."""
    return _profile_hook


def settrace(func):
    """Set a trace function for all threads started from the threading module."""
    global _trace_hook
    _trace_hook = func


def gettrace():
    """Get the trace function as set by threading.settrace()."""
    return _trace_hook


# Synchronization classes

Lock = _allocate_lock


class RLock(_Verbose):
    """Factory function that returns a new reentrant lock.

    A reentrant lock must be released by the thread that acquired it. Once a
    thread has acquired a reentrant lock, the same thread may acquire it again
    without blocking; the thread must release it once for each time it has
    acquired it.

    """
    if _CRLock is None:
        return _PyRLock(*args, **kwargs)
    return _CRLock(*args, **kwargs)


class _RLock:
    """This class implements reentrant lock objects."""

    def __init__(self):
        self._block = _allocate_lock()
        self._owner = None
        self._count = 0

    def __repr__(self):
        owner = self._owner
        try:
            owner = _active[owner].name
        except KeyError:
            pass
        return "<%s %s.%s object owner=%r count=%d at %s>" % (
            "locked" if self._block.locked() else "unlocked",
            self.__class__.__module__,
            self.__class__.__qualname__,
            owner,
            self._count,
            hex(id(self)),
        )

    def acquire(self, blocking=True, timeout=-1):
        """Acquire a lock, blocking or non-blocking."""
        me = get_ident()
        if self._owner == me:
            self._count += 1
            return 1
        rc = self._block.acquire(blocking, timeout)
        if rc:
            self._owner = me
            self._count = 1
        return rc

    __enter__ = acquire

    def release(self):
        """Release a lock, decrementing the recursion level."""
        if self._owner != get_ident():
            raise RuntimeError("cannot release un-acquired lock")
        self._count = count = self._count - 1
        if not count:
            self._owner = None
            self._block.release()

    def __exit__(self, t, v, tb):
        self.release()


_PyRLock = _RLock


class Condition:
    """Class that implements a condition variable."""

    def __init__(self, lock=None):
        if lock is None:
            lock = RLock()
        self._lock = lock
        self.acquire = lock.acquire
        self.release = lock.release
        self._waiters = _deque()

    def wait(self, timeout=None):
        """Wait until notified or until a timeout occurs."""
        if not self._lock.acquire(False):
            raise RuntimeError("cannot wait on un-acquired lock")
        waiter = _allocate_lock()
        waiter.acquire()
        self._waiters.append(waiter)
        self._lock.release()
        gotit = False
        try:
            if timeout is None:
                waiter.acquire()
                gotit = True
            else:
                gotit = waiter.acquire(True, timeout)
            return gotit
        finally:
            self._lock.acquire()
            if not gotit:
                try:
                    self._waiters.remove(waiter)
                except ValueError:
                    pass

    def notify(self, n=1):
        """Wake up one or more threads waiting on this condition."""
        if not self._lock.acquire(False):
            raise RuntimeError("cannot notify on un-acquired lock")
        waiters = self._waiters
        while waiters and n > 0:
            waiter = waiters.popleft()
            waiter.release()
            n -= 1

    def notify_all(self):
        """Wake up all threads waiting on this condition."""
        self.notify(len(self._waiters))


class Semaphore:
    """This class implements semaphore objects."""

    def __init__(self, value=1):
        if value < 0:
            raise ValueError("semaphore initial value must be >= 0")
        self._cond = Condition(Lock())
        self._value = value

    def acquire(self, blocking=True, timeout=None):
        """Acquire a semaphore, decrementing the internal counter by one."""
        if not blocking and timeout is not None:
            raise ValueError("can't specify timeout for non-blocking acquire")
        rc = False
        with self._cond:
            while self._value == 0:
                if not blocking:
                    break
                if timeout is not None:
                    timeout = max(timeout - _time(), 0)
                    if timeout <= 0:
                        break
            else:
                self._value -= 1
                rc = True
        return rc

    __enter__ = acquire

    def release(self, n=1):
        """Release a semaphore, incrementing the internal counter by one or more."""
        if n < 1:
            raise ValueError("n must be one or more")
        with self._cond:
            self._value += n
            for _ in range(n):
                self._cond.notify()

    def __exit__(self, t, v, tb):
        self.release()


class BoundedSemaphore(Semaphore):
    """Implements a bounded semaphore."""

    def __init__(self, value=1):
        super().__init__(value)
        self._initial_value = value

    def release(self, n=1):
        """Release a semaphore, incrementing the internal counter by one or more."""
        if n < 1:
            raise ValueError("n must be one or more")
        with self._cond:
            if self._value + n > self._initial_value:
                raise ValueError("Semaphore released too many times")
            self._value += n
            for _ in range(n):
                self._cond.notify()


class Event:
    """Class implementing event objects."""

    def __init__(self):
        self._cond = Condition(Lock())
        self._flag = False

    def is_set(self):
        """Return true if and only if the internal flag is true."""
        return self._flag

    def set(self):
        """Set the internal flag to true."""
        with self._cond:
            self._flag = True
            self._cond.notify_all()

    def clear(self):
        """Reset the internal flag to false."""
        with self._cond:
            self._flag = False

    def wait(self, timeout=None):
        """Block until the internal flag is true."""
        with self._cond:
            if not self._flag:
                self._cond.wait(timeout)
            return self._flag


class Thread:
    """A class that represents a thread of control."""

    def __init__(
        self,
        group: Optional[Any] = None,
        target: Optional[Callable[..., Any]] = None,
        name: Optional[str] = "",
        args: Tuple[Any, ...] = (),
        kwargs: Optional[Dict[str, Any]] = None,
        daemon: Optional[bool] = None,
    ) -> None:
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}
        self._name = str(name or _newname(self.__class__.__name__))
        self._daemon = daemon
        self._ident = None
        self._tstate_lock = None
        self._started = False

    def start(self):
        """Start the thread's activity."""
        if self._started:
            raise RuntimeError("Thread already started")
        self._started = True
        _thread.start_new_thread(self._bootstrap, ())

    def _bootstrap(self):
        """Internal method to bootstrap the thread."""
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        finally:
            self._started = False

    def join(self, timeout: Optional[float] = None):
        """Wait until the thread terminates."""
        if not self._started:
            return
        if self._tstate_lock:
            self._tstate_lock.acquire(timeout=timeout)


_counter = _count(1).__next__


def _newname(name_template):
    return name_template % _counter()


_active = {}
_limbo = {}
_dangling = WeakSet()

# Configure logging
logger = logging.getLogger(__name__)


class ThreadManager:
    """
    Custom thread manager for MAGUS PRIME X system.
    Provides enhanced thread creation, tracking, and management capabilities.
    """

    def __init__(self):
        """Initialize the thread manager"""
        # Use list explicitly to store active threads
        self.active_threads: List[threading.Thread] = list()
        self.thread_metadata: Dict[str, Dict[str, Any]] = {}
        self.stop_event = threading.Event()

    def create_thread(
        self,
        target: Callable,
        name: str,
        args: tuple = (),
        kwargs: dict = None,
        daemon: bool = True,
    ) -> threading.Thread:
        """
        Create and register a new thread

        Args:
            target: Function to run in the thread
            name: Thread name
            args: Arguments for the target function
            kwargs: Keyword arguments for the target function
            daemon: Whether the thread should be a daemon

        Returns:
            threading.Thread: The created thread
        """
        if kwargs is None:
            kwargs = {}

        thread = threading.Thread(
            target=target, name=name, args=args, kwargs=kwargs, daemon=daemon
        )

        # Store thread in our list of active threads
        self.active_threads.append(thread)

        # Add metadata
        self.thread_metadata[name] = {
            "created_at": time.time(),
            "status": "created",
            "daemon": daemon,
        }

        logger.info(f"Created thread: {name}")
        return thread

    def start_thread(self, thread_name: str) -> bool:
        """Start a registered thread by name"""
        for thread in self.active_threads:
            if thread.name == thread_name:
                if not thread.is_alive():
                    thread.start()
                    self.thread_metadata[thread_name]["status"] = "running"
                    logger.info(f"Started thread: {thread_name}")
                    return True
                else:
                    logger.warning(f"Thread already running: {thread_name}")
                    return False

        logger.error(f"Thread not found: {thread_name}")
        return False

    def stop_all_threads(self) -> None:
        """Signal all threads to stop and clean up"""
        self.stop_event.set()
        logger.info("Stop event set for all threads")

        # Convert to list for thread-safe iteration since we'll modify active_threads
        active_thread_names = [t.name for t in self.active_threads]

        for thread_name in active_thread_names:
            self.cleanup_thread(thread_name)

    def cleanup_thread(self, thread_name: str) -> bool:
        """Remove a thread from tracking"""
        for i, thread in enumerate(self.active_threads):
            if thread.name == thread_name:
                # Remove from our list
                del self.active_threads[i]

                # Update metadata
                if thread_name in self.thread_metadata:
                    self.thread_metadata[thread_name]["status"] = "cleaned"

                logger.info(f"Cleaned up thread: {thread_name}")
                return True

        return False

    def get_active_thread_count(self) -> int:
        """Get the number of active threads"""
        # Use the list's len() method
        return len(self.active_threads)

    def get_thread_status(self, thread_name: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific thread"""
        for thread in self.active_threads:
            if thread.name == thread_name:
                status = self.thread_metadata.get(thread_name, {}).copy()
                status["is_alive"] = thread.is_alive()
                return status

        return None

    def get_all_thread_status(self) -> List[Dict[str, Any]]:
        """Get status of all threads"""
        # Use List type hint for the return value to explicitly use the imported list type
        result: List[Dict[str, Any]] = []

        for thread in self.active_threads:
            thread_name = thread.name
            status = self.thread_metadata.get(thread_name, {}).copy()
            status["name"] = thread_name
            status["is_alive"] = thread.is_alive()
            result.append(status)

        return result


# Create a global instance
thread_manager = ThreadManager()


# Helper functions to make thread management easier
def create_and_start_thread(
    target: Callable,
    name: str,
    args: tuple = (),
    kwargs: dict = None,
    daemon: bool = True,
) -> threading.Thread:
    """Create and start a managed thread in one call"""
    thread = thread_manager.create_thread(target, name, args, kwargs, daemon)
    thread.start()
    return thread


def stop_all_threads():
    """Stop all managed threads"""
    thread_manager.stop_all_threads()


def get_thread_count() -> int:
    """Get current number of active threads"""
    return thread_manager.get_active_thread_count()

# Add implementations for missing functions/classes
active_count = threading.active_count
current_thread = threading.current_thread
main_thread = threading.main_thread
Barrier = threading.Barrier
BrokenBarrierError = threading.BrokenBarrierError
Timer = threading.Timer
local = threading.local
stack_size = _thread.stack_size
excepthook = threading.excepthook
ExceptHookArgs = threading.ExceptHookArgs

def stack_size(size=None):
    """Return the thread stack size used when creating new threads.

    The optional size argument specifies the stack size (in bytes) to be used
    for subsequently created threads, and must be 0 (use platform or
    configured default) or a positive integer value of at least 32,768 (32k).
    If changing the thread stack size is unsupported, a ThreadError is
    raised. If the specified size is invalid, a ValueError is raised.

    Note that some platforms may specify that the stack size be a multiple of
    the system's page size.

    """
    if size is None:
        return _thread.stack_size()
    return _thread.stack_size(size)
