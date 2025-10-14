"""
Instantiates class to fetch spot prices.
"""

import ujson
import machine
import gc
import urequests
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

    def get_prices(self, utc_time):
        # type: (datetime) -> None

        """
        Fetch prices and DST offset from API and write them to files.
        Writes:
            prices_today.json: Today's prices
            prices_tomorrow.json: Tomorrow's prices
            dst_offset.json: DST offset information
        """
        failure_count = 0
        today = (utc_time.year, utc_time.month, utc_time.day)
        tomorrow_time = utc_time + timedelta(hours=24)
        tomorrow = (tomorrow_time.year, tomorrow_time.month, tomorrow_time.day)

        for url, day in zip(self.get_url(), self.days):

            print(f"Fetching JSON from: {url}")
            response = urequests.get(url)

            if response.status_code == 200:
                data = response.json()

                # Extract prices and time_end data
                prices = [item["SEK_per_kWh"] for item in data]
                time_ends = [item["time_end"] for item in data]

                print(prices)

                # Determine if this is today or tomorrow and write to appropriate file
                day_tuple = (day.year, day.month, day.day)
                if day_tuple == today:
                    # Write today's prices
                    with open("prices_today.json", "w") as f:
                        ujson.dump(prices, f)
                    # Write DST offset for today
                    dst_offset = self._get_dst_offset_from_times(time_ends)
                    with open("dst_offset.json", "w") as f:
                        ujson.dump(dst_offset, f)
                elif day_tuple == tomorrow:
                    # Write tomorrow's prices
                    with open("prices_tomorrow.json", "w") as f:
                        ujson.dump(prices, f)

                # Clear variables to free memory
                del data, prices, time_ends

            else:
                print(
                    f"Failed to fetch JSON for day {day.day}, status code: {response.status_code}. Prices might not be available yet."
                )
                failure_count += 1
                if failure_count == 2:
                    print("Failed to fetch JSON twice, rebooting...")
                    machine.soft_reset()
            response.close()
            gc.collect()

        print("Response received!")

        return self._from_file()

    def _get_dst_offset_from_times(self, time_ends):
        # type: (list) -> int
        """
        Get the Daylight Saving Time (DST) offset from time_end list.
        Args:
            time_ends (list): List of time_end strings.
        Returns:
            int: The DST offset in hours.
        """
        last_time_end = time_ends[-1]
        tz_part = last_time_end.partition("+0")[2]
        dst_offset = int(tz_part[0]) if tz_part and tz_part[0].isdigit() else None

        return dst_offset

    def _from_file(self):
        # type: () -> tuple
        """
        Read electricity prices and DST offset from JSON files.

        This method reads the previously saved data from the filesystem:
        - prices_today.json: Today's electricity prices (list of floats)
        - prices_tomorrow.json: Tomorrow's electricity prices (list of floats)
        - dst_offset.json: Current DST offset in hours (int)

        Returns:
            tuple: (prices_today, prices_tomorrow, dst_offset)
                - prices_today (list or None): List of today's prices or None if file missing
                - prices_tomorrow (list or None): List of tomorrow's prices or None if file missing
                - dst_offset (int): DST offset in hours, defaults to 1 (CET) if file missing
        """
        # Read prices and DST offset from files
        try:
            with open("prices_today.json", "r") as f:
                prices_today = ujson.load(f)
        except (OSError, ValueError):
            prices_today = None

        try:
            with open("prices_tomorrow.json", "r") as f:
                prices_tomorrow = ujson.load(f)
        except (OSError, ValueError):
            prices_tomorrow = None

        try:
            with open("dst_offset.json", "r") as f:
                dst_offset = ujson.load(f)
        except (OSError, ValueError):
            dst_offset = 1  # Fallback to CET
            print("Could not read dst_offset.json, using CET fallback (UTC+1)")

        return prices_today, prices_tomorrow, dst_offset

    # Debug TLS connection and save to file

    # def _to_file(self, url, filename="response.json"):

    #     proto, _, rest = url.partition("://")
    #     host, _, path = rest.partition("/")
    #     if not path:
    #         path = ""
    #     path = "/" + path

    #     ctx = tls.SSLContext(tls.PROTOCOL_TLS_CLIENT)
    #     ctx.verify_mode = tls.CERT_NONE

    #     addr = socket.getaddrinfo(host, 443)[0][-1]
    #     s = socket.socket()
    #     s.connect(addr)
    #     sx = ctx.wrap_socket(s, server_side=False, server_hostname=host)

    #     headers = (
    #         f"GET {path} HTTP/1.1\r\n"
    #         f"Host: {host}\r\n"
    #         "User-Agent: Mozilla/5.0 (ESP32; MicroPython)\r\n"
    #         "Accept: application/json\r\n"
    #         "Connection: close\r\n\r\n"
    #     )
    #     sx.write(headers.encode())

    #     # --- Read headers first ---
    #     buf = b""
    #     while b"\r\n\r\n" not in buf:
    #         buf += sx.read(128)
    #     header, body = buf.split(b"\r\n\r\n", 1)
    #     print(header.decode())

    #     # --- Stream body to file ---
    #     with open(filename, "wb") as f:
    #         f.write(body)
    #         while True:
    #             chunk = sx.read(1024)
    #             if not chunk:
    #                 break
    #             f.write(chunk)

    #     sx.close()
    #     s.close()
    #     print("Saved to", filename)
