import functools
import os

# Set to True to enable function logging, or False to disable
ENABLE_FUNCTION_LOGGING = False


def PrintFunctionName(func):
    """Decorator that prints 'filename: function_name' when enabled."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if ENABLE_FUNCTION_LOGGING:
            filename = os.path.basename(func.__code__.co_filename)
            print(f"{filename}: {func.__name__}")
        return func(*args, **kwargs)

    return wrapper
