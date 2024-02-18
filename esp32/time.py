"""
Replace standard time.localtime()

For more information about extending built in libraries, see:
https://docs.micropython.org/en/latest/library/index.html#extending-built-in-libraries-from-python
"""

import sys

_path = sys.path
sys.path = ()

try:
    from time import *
finally:
    sys.path = _path
    del _path


def localtime(secs: int | None = None) -> tuple[int, int, int, int, int, int, int, int]:
    """Returns Swedish local time.

    According to [Wikipedia](https://en.wikipedia.org/wiki/Time_in_Sweden)
    does Sweden observe daylight saving time
    from: the last Sunday in March (02:00 CET)
    to:   the last Sunday in October (03:00 CEST)
    """

    def last_sunday(year: int, month: int, hour: int, minute: int) -> int:
        """Get the time of the last sunday of the month
        It returns an integer which is the number of seconds since Jan 1, 2000, just like mktime().
        """

        # Get the UTC time of the last day of the month
        seconds = mktime((year, month + 1, 0, hour, minute, 0, None, None))

        # Calculate the offset to the last sunday of the month
        (year, month, mday, hour, minute, second, weekday, yearday) = gmtime(seconds)
        offset = (weekday + 1) % 7

        # Return the time of the last sunday of the month
        return mktime((year, month, mday - offset, hour, minute, second, None, None))

    utc = gmtime(secs)

    # Find start date for daylight saving, i.e. last Sunday in March (01:00 UTC)
    start_secs = last_sunday(year=utc[0], month=3, hour=1, minute=0)

    # Find stop date for daylight saving, i.e. last Sunday in October (01:00 UTC)
    stop_secs = last_sunday(year=utc[0], month=10, hour=1, minute=0)

    utc_secs = mktime(utc)
    if utc_secs >= start_secs and utc_secs < stop_secs:
        delta_secs = 2 * 60 * 60  # Swedish summer time (CEST or UTC + 2h)
    else:
        delta_secs = 1 * 60 * 60  # Swedish normal time (CET or UTC + 1h)

    return gmtime(utc_secs + delta_secs)
