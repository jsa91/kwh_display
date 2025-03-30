"""
A module to handle Swedish local time with consideration for daylight saving time.

This module includes a class to:
- Initialize the Swedish timezone with DST consideration
- Get the current local time in Sweden
"""

import ntptime
import machine
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

        print("Synchronizing time with NTP server...")
        ntptime.timeout = 3
        try:
            ntptime.settime()
            print("UTC time synchronized successfully!")
        except OSError as e:
            print(f"Failed to sync time: {e}")
            machine.soft_reset()

        now = datetime.now(timezone(timedelta()))

        print(f"UTC time is: {now}")

        # Determine if DST is in effect
        self.offset = self._determine_offset(now)

    def _determine_offset(self, now):
        # type: (datetime) -> int
        """
        Determine the Swedish timezone offset considering DST.

        Args:
            now (datetime): The current datetime.

        Returns:
            int: The timezone offset.
        """
        utc_offset = 1  # Standard time
        dst_offset = 2  # Daylight saving time

        month, day = now.month, now.day
        weekday = now.weekday()

        # FIXME: Correct DST calculation.
        # if (
        #     (month > 3 and month < 10)
        #     or (month == 3 and day - weekday >= 25)
        #     or (month == 10 and day - weekday < 25)
        # ):
        #     print("Daylight saving time is in effect.")
        #     return dst_offset
        # else:
        #     print("Standard time is in effect.")
        #     return utc_offset

        print("Daylight saving time is in effect.")
        return dst_offset

    def swe_localtime(self):
        # type: () -> datetime
        """
        Get the current local time in Sweden.

        Returns:
            datetime: The current local time in Sweden.
        """
        return datetime.now(timezone(timedelta(hours=self.offset)))
