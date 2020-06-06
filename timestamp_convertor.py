import time

TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"


def ts_to_time(timestamp):
    return time.strptime(timestamp, TIMESTAMP_FORMAT)


def time_to_ts(t):
    return time.strftime(TIMESTAMP_FORMAT, t)

    