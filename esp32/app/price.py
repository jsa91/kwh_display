"""
Instantiates class to fetch spot prices.
"""

import urequests
import ujson
import machine
from app.ili9341 import GUI
from datetime import timedelta


class ElectricityPriceAPI:
    """
    Fetch spot prices.
    """

    def __init__(self, utc_time):
        # type: (datetime) -> None
        """
        Initialize the ElectricityPriceAPI instance by loading the configuration.
        """
        with open("config.json", "r") as f:
            self.config = ujson.load(f)

        self.days = (utc_time, utc_time + timedelta(hours=24))

    def get_url(self):
        # type: () -> list
        """
        Get the URL for the API.

        Returns:
            list: A list of URLs for fetching the electricity prices.
        """
        return [
            f"{self.config['url']}{self.config['api']}{day.year:04}/{day.month:02}-{day.day:02}_{self.config['zone']}.json"
            for day in self.days
        ]

    def get_url_tomorrow(self, swe_localtime):
        # type: (datetime) -> str
        """
        Get the URL for the API for tomorrow which causes desplay to reboot.

        Returns:
            str: A URL for fetching the electricity prices for tomorrow.

        """

        tomorrow = swe_localtime + timedelta(hours=24)

        return f"{self.config['url']}{self.config['api']}{tomorrow.year:04}/{tomorrow.month:02}-{tomorrow.day:02}_{self.config['zone']}.json"

    def _get_dst_offset(self, dst_offsets, today):
        # type: (dict, tuple) -> int
        """
        Get the Daylight Saving Time (DST) offset for today.
        Args:
            dst_offsets (dict): Dictionary containing DST offsets for each day.
            today (tuple): Tuple representing today's date (year, month, day).
        Returns:
            int: The DST offset in hours.
        """
        last_time_end = dst_offsets[str(today)][-1]
        tz_part = last_time_end.partition("+0")[2]
        dst_offset = int(tz_part[0]) if tz_part and tz_part[0].isdigit() else None
        print(
            f"Time offset is {dst_offset} hours, {'DST is effect.' if dst_offset == 2 else 'CET in effect.'}"
        )

        return dst_offset

    def _add_fees(self, price_list, fees_list):
        # type: (list, list) -> list
        """
        Add configured fees to each price in the list.

        Args:
            price_list (list): List of prices.

        Returns:
            list: List of prices with fees added, or original list if add_fees is False.
        """
        # Ensure fees_list matches price_list length
        if len(fees_list) != len(price_list):
            e = "Length of fees list does not match price list!"
            GUI.set_error(e)
            raise ValueError(e)

        return [price + fee for price, fee in zip(price_list, fees_list)]

    def get_prices(self, utc_time):
        # type: (datetime) -> tuple

        """
        Fetch prices and DST offset from API.
        Returns:
            tuple: (prices_today, prices_tomorrow, dst_offset)
        """
        prices = {}
        dst_offsets = {}
        failure_count = 0

        for url, day in zip(self.get_url(), self.days):

            print(f"Fetching JSON from: {url}")
            response = urequests.get(url)
            if response.status_code == 200:
                data = response.json()
                key = str((day.year, day.month, day.day))
                prices[key] = [item["SEK_per_kWh"] for item in data]
                dst_offsets[key] = [item["time_end"] for item in data]
            else:
                print(
                    f"Failed to fetch JSON for day {day.day}, status code: {response.status_code}. Prices might not be available yet."
                )
                failure_count += 1
                if failure_count == 2:
                    print("Failed to fetch JSON twice, rebooting...")
                    machine.soft_reset()
            response.close()

        today = (utc_time.year, utc_time.month, utc_time.day)
        tomorrow_time = utc_time + timedelta(hours=24)
        tomorrow = (tomorrow_time.year, tomorrow_time.month, tomorrow_time.day)
        prices_today = prices.get(str(today))
        prices_tomorrow = prices.get(str(tomorrow))

        if self.config.get("add_fees", True):
            if prices_today is not None:
                prices_today = self._add_fees(prices_today, self.config.get("fees"))
            if prices_tomorrow is not None:
                prices_tomorrow = self._add_fees(
                    prices_tomorrow, self.config.get("fees")
                )

        return prices_today, prices_tomorrow, self._get_dst_offset(dst_offsets, today)
