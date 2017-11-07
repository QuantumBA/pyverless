from functools import wraps

from pyverless.config import settings


def warmup(func):
    """
    Decorator for handler functions that provides fast exit when warm-up is
    performed via serverless-plugin warmup
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        event = args[0]

        if event.get('source') == 'serverless-plugin-warmup':
            if settings.WARMUP_LOG:
                print('warmup sucessful')
            return None

        return func(*args, **kwargs)

    return wrapper
