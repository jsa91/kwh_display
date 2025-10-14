"""
A module to handle Swedish local time with consideration for daylight saving time.

This module includes a class to:
- Initialize the Swedish timezone with DST consideration
- Get the current local time in Sweden
"""

import ntptime
import machine
import time
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
            time.sleep(3)
            machine.soft_reset()

        print(f"UTC time is: {datetime.now(timezone(timedelta()))}")

    @staticmethod
    def utc_time():
        # type: () -> datetime
        """
        Get the current UTC time.

        Returns:
            datetime: The current UTC time.
        """
        return datetime.now(timezone(timedelta()))

    @staticmethod
    def swe_localtime(dst_offset):
        # type: (int) -> datetime
        """
        Get the current local time in Sweden.

        Returns:
            datetime: The current local time in Sweden.
        """

        return datetime.now(timezone(timedelta(hours=dst_offset)))
