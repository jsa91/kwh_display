"""
Utility functions for network operations, time synchronization, and fetching electricity prices.

This module includes functions to:
- Connect to WiFi
- Enable a hotspot
- Synchronize time with an NTP server
- Fetch electricity prices from a file
- Update the display with current prices
"""

from datetime import timedelta
import ujson
import network
import ntptime
import machine
import urequests


def wifi():
    # type: () -> None
    """
    Connect to WiFi according to config file.
    """
    network.WLAN(network.AP_IF).active(False)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm=0)
    wlan.config(txpower=20)
    if not wlan.isconnected():
        with open("config.json", "r") as f:
            config = ujson.load(f)
        print(f"Connecting to {config['ssid']}...")
        wlan.connect(config["ssid"], config["password"])
        while not wlan.isconnected():
            pass
    print(f"Connected! {wlan.ifconfig()}")


def hotspot():
    # type: () -> None
    """
    Enable hotspot @ 192.168.4.1
    Primarily for FTP connection.
    """
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="kwh_display")
    while ap.active() is False:
        pass
    print(f"Access Point @ {ap.ifconfig()}")


def ntp_sync():
    # type: () -> None
    """
    Sync UTC time with NTP
    """
    print("Synchronizing time with NTP server...")
    ntptime.timeout = 3
    for _ in range(3):  # Try sync time three times before reset
        try:
            ntptime.settime()
            print("UTC time synchronized successfully!")
            return
        except OSError as e:
            print(f"Failed to sync time: {e}")
            machine.soft_reset()

def fetch_prices_from_file(api, time):
    # type: (ElectricityPriceAPI, SweTime) -> tuple
    """
    Fetch prices from the file.

    Args:
        api (ElectricityPriceAPI): The API instance to fetch prices.

    Returns:
        tuple: A tuple containing prices for today and tomorrow.
    """
    api.get_prices()

    with open("prices.json", "r") as f:
        prices = ujson.load(f)

    current_time = time.swe_localtime()
    today = (current_time.year, current_time.month, current_time.day)
    h24_offset = current_time + timedelta(hours=24)
    tomorrow = (h24_offset.year, h24_offset.month, h24_offset.day)

    prices_today = prices[0][str(today)] if prices[0] else None
    prices_tomorrow = prices[1][str(tomorrow)] if len(prices) > 1 else None

    return prices_today, prices_tomorrow


def update_display(
    gui, prices_today, prices_tomorrow, current_hour, api, swe_localtime
):
    # type: (GUI, dict, dict, int, ElectricityPriceAPI, datetime) -> int
    """
    Update the display with the current prices.

    Args:
        gui (GUI): The GUI instance to update.
        prices_today (dict): The prices for today.
        prices_tomorrow (dict): The prices for tomorrow.
        current_hour (int): The current hour.
        api (ElectricityPriceAPI): The API instance to fetch prices.
        swe_localtime (datetime): The current local time in Sweden.

    Returns:
        int: The current hour.
    """

    hour = swe_localtime.hour
    minute = swe_localtime.minute

    if hour != current_hour:
        if hour == 0:
            prices_today = prices_tomorrow
            prices_tomorrow = None
            gui.plot_prices(prices_today, prices_tomorrow)

        gui.set_price(hour, prices_today)
        gui.set_arrow(hour)

    if hour >= 13 and prices_tomorrow is None:
        print(f"Checking if new prices are available @ {hour}:{minute}...")
        response = urequests.get(api.get_url()[1])
        if response.status_code != 404:
            print(f"New prices available, rebooting @ {hour}:{minute}...")
            machine.soft_reset()
        response.close()

    return hour, prices_today, prices_tomorrow
