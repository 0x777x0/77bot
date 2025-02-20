import time
from datetime import datetime, timedelta


def get_timestamp():
    current_time_seconds = time.time()
    return int(current_time_seconds * 1000)


def get_start_time():
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_of_day


def get_end_time():
    now = datetime.now()
    end_of_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
    return end_of_day
