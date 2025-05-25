import logging
import random
import time
from typing import Callable, Any, Tuple, Type
from functools import wraps

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_strategy: str = 'exponential',
    retry_exceptions: Tuple[Type[Exception]] = (Exception,),
    log_info: bool = True
):
    """
    Decorator to retry a function call upon failure.

    Args:
        max_retries (int): Maximum number of retry attempts. Defaults to 3.
        delay (float): Initial delay between retries in seconds. Defaults to 1.0.
        backoff_strategy (str): Strategy for increasing delay between retries.
            Options: 'exponential', 'linear', 'fixed'. Defaults to 'exponential'.
        retry_exceptions (Tuple[Type[Exception]]): 
            Exception types that trigger a retry. Defaults to (Exception,).
        log_info (bool): Whether to log retry attempts. Defaults to True.

    Returns:
        Callable: The decorated function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        if log_info:
                            logging.error(f"Function {func.__name__} failed after {max_retries} attempts: {str(e)}", exc_info=True)
                        raise
                    else:
                        if backoff_strategy == 'exponential':
                            sleep_time = delay * (2 ** attempt) + random.uniform(0, 0.5)
                        elif backoff_strategy == 'linear':
                            sleep_time = delay * (attempt + 1) + random.uniform(0, 0.5)
                        elif backoff_strategy == 'fixed':
                            sleep_time = delay + random.uniform(0, 0.5)
                        else:
                            sleep_time = delay + random.uniform(0, 0.5)
                            logging.warning(f"Unknown backoff strategy '{backoff_strategy}'. Using fixed delay.")
                        if log_info:
                            logging.info(f"Function {func.__name__} attempt {attempt + 1} failed. Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
            return None
        return wrapper
    return decorator
