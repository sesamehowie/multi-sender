import functools
from loguru import logger
from ..helpers.helpers import sleeping
from ...config.constants import MAX_RETRIES


def retry_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(MAX_RETRIES):
            try:
                res = func(*args, **kwargs)
                return res
            except Exception as e:
                logger.warning(f"{func.__name__} - exception: {str(e)}")
                if "insufficient funds" in str(e):
                    return
                sleeping(mode=1)
        else:
            return

    return wrapper
