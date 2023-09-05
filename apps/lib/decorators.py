import logging
import time

logger = logging.getLogger(__name__)


def timer(func):
    def timer_wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed_time = (end - start) / 60
        logger.debug(f"Elapsed time: {round(elapsed_time)} minutes...{args}")
        return result

    return timer_wrapper
