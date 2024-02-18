"""
Instantiates class to fetch spot prices.
"""

import time
import urequests
import ujson


class ElectricityPriceAPI:
    """
    Fetch spot prices.
    """

    def __init__(self):
        with open("config.json", "r") as f:
            self.config = ujson.load(f)

    def get_prices(self):
        """
        Create json file, fetch prices from API and append to file.
        """

        # Today and tomorrow
        days = (time.localtime(), time.localtime(time.time() + 86400))

        # Clear the price data
        with open("prices.json", "w"):
            pass

        json_prices = []

        for day in days:

            year, month, date = (
                "{:04}".format(day[0]),
                "{:02}".format(day[1]),
                "{:02}".format(day[2]),
            )

            request = f"{self.config['url']}{self.config['api']}{year}/{month}-{date}_{self.config['zone']}.json"

            print(f"Fetching JSON from: {request}")
            response = urequests.get(request)

            if response.status_code == 200:
                json_data = response.json()
            else:
                print(
                    f"Failed to fetch JSON, status code: {response.status_code}\nPrices might not be published yet."
                )
                continue

            prices = {str(day[0:3]): [price["SEK_per_kWh"] for price in json_data]}

            json_prices.append(prices)

            print(prices)

        with open("prices.json", "a") as f:
            ujson.dump(json_prices, f)
