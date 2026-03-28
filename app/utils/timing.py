"""
Timing/Profiling utility for measuring startup performance
"""
import time
import logging
from functools import wraps
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)

# Global start time
_startup_start_time: Optional[float] = None


def init_startup_timer():
    """Initialize the startup timer - call this at app start"""
    global _startup_start_time
    _startup_start_time = time.time()
    return _startup_start_time


def get_elapsed_time() -> float:
    """Get elapsed time since startup init"""
    if _startup_start_time is None:
        return 0.0
    return time.time() - _startup_start_time


def log_timing(message: str, level: int = logging.INFO):
    """Log a message with elapsed time since startup"""
    elapsed = get_elapsed_time()
    logger.log(level, f"[T+{elapsed:6.3f}s] {message}")


def timed_function(log_level: int = logging.INFO):
    """
    Decorator to log function execution time
    
    Usage:
        @timed_function
        def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            start = time.time()
            log_timing(f"▶ START: {func_name}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                logger.log(log_level, f"[T+{get_elapsed_time():6.3f}s] ✓ DONE: {func_name} ({elapsed:.3f}s)")
                return result
            except Exception as e:
                elapsed = time.time() - start
                logger.log(log_level, f"[T+{get_elapsed_time():6.3f}s] ✗ ERROR: {func_name} ({elapsed:.3f}s) - {e}")
                raise
        return wrapper
    return decorator


@contextmanager
def timed_block(block_name: str, log_level: int = logging.INFO):
    """
    Context manager to time a block of code
    
    Usage:
        with timed_block("Initialization"):
            # code to time
    """
    start = time.time()
    log_timing(f"▶ BLOCK START: {block_name}")
    try:
        yield
        elapsed = time.time() - start
        logger.log(log_level, f"[T+{get_elapsed_time():6.3f}s] ✓ BLOCK DONE: {block_name} ({elapsed:.3f}s)")
    except Exception as e:
        elapsed = time.time() - start
        logger.log(log_level, f"[T+{get_elapsed_time():6.3f}s] ✗ BLOCK ERROR: {block_name} ({elapsed:.3f}s) - {e}")
        raise
