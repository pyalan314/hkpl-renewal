import functools
import time

import schedule
from loguru import logger
from requests import RequestException
from tenacity import retry, retry_if_exception_type, stop_after_delay, wait_fixed, RetryCallState

import notify
import renew


def safe(exit_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                job_func(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
                notify.send_fail(e)
                if exit_on_failure:
                    exit()
            else:
                logger.info('Job complete')
        return wrapper
    return catch_exceptions_decorator


def retry_log(state: RetryCallState):
    logger.error(str(state))


@safe(exit_on_failure=True)
@retry(retry=retry_if_exception_type(RequestException), stop=stop_after_delay(300), wait=wait_fixed(10), after=retry_log)
def task():
    renew.main()


if __name__ == '__main__':
    schedule.every().day.at("09:00").do(task)
    schedule.run_all()
    schedule.every().day.at("21:00").do(task)
    while True:
        schedule.run_pending()
        time.sleep(60)
