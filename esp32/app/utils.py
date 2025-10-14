"""
Utility functions for network operations, time synchronization, and fetching electricity prices.

This module includes functions to:
- Connect to WiFi
- Enable a hotspot
- Synchronize time with an NTP server
- Fetch electricity prices from a file
- Update the display with current prices
"""

import ujson
import network
import machine
import urequests
from app.ili9341 import GUI


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
        try:
            with open("config.json", "r") as f:
                config = ujson.load(f)
        except ValueError as e:
            print(f"Error reading config file: {e}")
            GUI.set_error(e)
            raise

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


def update_display(
    gui, prices_today, prices_tomorrow, current_15min, api, swe_localtime
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
    second = swe_localtime.second
    upcoming_15min = (hour * 4) + (minute // 15)

    if upcoming_15min != current_15min:
        if upcoming_15min == 0:
            prices_today = prices_tomorrow
            prices_tomorrow = None
            gui.plot_prices(prices_today, prices_tomorrow)

        gui.set_price(upcoming_15min, prices_today)
        gui.set_arrow(hour)

    # Checking if new prices are available.
    if hour >= 13 and prices_tomorrow is None:
        try:
            response = urequests.get(api.get_url_tomorrow(swe_localtime))
            if response.status_code == 200:
                print(
                    f"New prices available, rebooting and fetching from: {api.get_url_tomorrow(swe_localtime)} @ {hour}:{minute}:{second}..."
                )
                machine.soft_reset()
            response.close()
        except OSError as e:
            print(f"Connection failed: {e}\nRebooting...")
            machine.soft_reset()

    return upcoming_15min, prices_today, prices_tomorrow
