from functools import wraps
from enum import Enum
from datetime import datetime


def custom_circuitbreaker(func, service_name="Service", threshold=5, timeout=3):
    @wraps(func)
    def cb(*args, **kwargs):
        def to_open():
            cb.state = STATE.OPEN
            cb.timestamp = datetime.now().timestamp()

        def to_close():
            cb.state = STATE.CLOSE
            cb.fail_count = 0

        def to_half_open():
            cb.state = STATE.HALF_OPEN
            cb.fail_count = 0
            cb.timestamp = 0
            cb.requests_since_startup = 0

        if (
            cb.state == STATE.HALF_OPEN
            and cb.fail_count == 0
            and cb.requests_since_startup == cb.threshold
        ):
            to_close()

        if (
            cb.state == STATE.OPEN
            and datetime.now().timestamp() >= cb.timestamp + timeout
        ):
            to_half_open()

        if cb.state == STATE.CLOSE and cb.fail_count >= cb.threshold:
            to_open()
            return f"{service_name} is currently not available", 503

        if cb.state == STATE.CLOSE or (
            cb.state == STATE.HALF_OPEN and cb.requests_since_startup % 5 == 0
        ):
            try:
                res = func(*args, **kwargs)
                cb.fail_count = 0
                cb.requests_since_startup += 1
                return res
            except:
                if cb.state == STATE.HALF_OPEN:
                    to_open()
                cb.fail_count += 1
                return f"{service_name} is currently not available", 503
        else:
            return f"{service_name} is currently not available", 503

    class STATE(Enum):
        OPEN = "OPEN"
        CLOSE = "CLOSE"
        HALF_OPEN = "HALF_OPEN"

    cb.state = STATE.CLOSE
    cb.threshold = threshold
    cb.fail_count = 0
    cb.timestamp = 0
    cb.requests_since_startup = 0
    return cb
