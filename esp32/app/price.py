"""
Instantiates class to fetch spot prices.
"""

import urequests
import ujson
import machine
from datetime import timedelta


class ElectricityPriceAPI:
    """
    Fetch spot prices.
    """

    def __init__(self, swe_localtime):
        # type: (datetime) -> None
        """
        Initialize the ElectricityPriceAPI instance by loading the configuration.
        """
        with open("config.json", "r") as f:
            self.config = ujson.load(f)

        self.days = (swe_localtime, swe_localtime + timedelta(hours=24))

    def get_url(self):
        # type: () -> list
        """
        Get the URL for the API.

        Returns:
            list: A list of URLs for fetching the electricity prices.
        """
        # Clear the price data
        with open("prices.json", "w"):
            pass

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

    def get_prices(self):
        # type: () -> None
        """
        Create json file, fetch prices from API and append to file.
        """

        send_to_file = []
        failure_count = 0

        for request, day in zip(self.get_url(), self.days):

            print(f"Fetching JSON from: {request}")
            response = urequests.get(request)

            if response.status_code == 200:
                send_to_file.append(
                    {
                        str((day.year, day.month, day.day)): [
                            price["SEK_per_kWh"] for price in response.json()
                        ]
                    }
                )
                response.close()
            else:
                print(
                    f"Failed to fetch JSON, status code: {response.status_code}\nPrices might not be published yet or URL is incorrect."
                )
                response.close()
                failure_count += 1  # Increment the counter on failure
                if failure_count == 2:
                    print("Failed to fetch JSON twice, rebooting...")
                    machine.soft_reset()
                continue

        print(send_to_file)
        with open("prices.json", "a") as f:
            ujson.dump(send_to_file, f)
