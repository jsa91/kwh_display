"""
A module to handle Swedish local time with consideration for daylight saving time.

This module includes a class to:
- Initialize the Swedish timezone with DST consideration
- Get the current local time in Sweden
"""

from datetime import datetime, timezone, timedelta


class SweTime:
    """
    A class to handle Swedish local time with consideration for daylight saving time.
    """

    def __init__(self):
        # type: () -> None
        """
        Initialize the SweTime class and set the timezone.
        """

        # Swedish timezone offset
        utc_offset = 1  # Standard time
        dst_offset = 2  # Daylight saving time

        # Determine if DST is in effect
        now = datetime.now(timezone(timedelta()))
        month, day = now.month, now.day
        weekday = now.weekday()

        if (
            (month > 3 and month < 10)
            or (month == 3 and day - weekday >= 25)
            or (month == 10 and day - weekday < 25)
        ):
            offset = dst_offset
        else:
            offset = utc_offset

        self.offset = offset

    def swe_localtime(self):
        # type: () -> datetime
        """
        Get the current local time in Sweden.

        Returns:
            datetime: The current local time in Sweden.
        """
        return datetime.now(timezone(timedelta(hours=self.offset)))
