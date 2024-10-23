import functools
from typing import Callable
from logger import file_handler

def log_file_operation(func: Callable) -> Callable:
    """
    Decorator to log file operations.

    This decorator wraps file operation functions to log their execution,
    including start, completion, and any errors that occur during the operation.

    Args:
        func (Callable): The file operation function to be decorated.

    Returns:
        Callable: The wrapped function that includes logging.

    Raises:
        None: This decorator doesn't raise exceptions directly, but re-raises
        any exceptions caught during the execution of the decorated function.

    Example:
        >>> @log_file_operation
        ... def read_file(filename):
        ...     with open(filename, 'r') as f:
        ...         return f.read()
        >>> content = read_file('example.txt')
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            file_handler.debug(f"Starting file operation: {func.__name__}")
            result = func(*args, **kwargs)
            file_handler.debug(f"Completed file operation: {func.__name__}")
            return result
        except Exception as e:
            file_handler.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

