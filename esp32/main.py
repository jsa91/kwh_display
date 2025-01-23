"""
This is a project developed in MicroPython aimed at creating a 
compact display solution using an ESP32 and an ILI9341 screen. 
The primary functionality of this project is to fetch 
electricity price data via API and display it on the screen.
"""

import os
import gc
import time as pytime
from app import utils
from app.swe_time import SweTime
from app.price import ElectricityPriceAPI
from app.ili9341 import GUI
from gui.core.colors import RED, YELLOW
from gui.core.nanogui import refresh
from gui.color_setup import ssd


def main():
    # type: () -> None
    """
    Initialise classes for fetching spot prices and displaying objects.
    Run scheduling with clock.
    """
    if "config.json" not in os.listdir():
        utils.hotspot()
        from ftp import uftpd

        print("Config file missing. Access through FTP to manage filesystem.")

    else:
        utils.wifi()
        utils.ntp_sync()

        time = SweTime()
        current_hour = time.swe_localtime().hour

        api = ElectricityPriceAPI()
        prices_today, prices_tomorrow = utils.fetch_prices_from_file(api, time)

        gui = GUI()
        gui.plot_prices(prices_today, prices_tomorrow)
        gui.set_price(current_hour, prices_today)
        gui.set_arrow(current_hour)
        uv, pi, days, months, dial, hrs, mins, secs, hstart, mstart, sstart = (
            gui.set_clock()
        )

        print(
            f"Boot sequence completed @ {time.swe_localtime().year}-{time.swe_localtime().month}-{time.swe_localtime().day} {time.swe_localtime().hour}:{time.swe_localtime().minute}:{time.swe_localtime().second}"
        )

        gc.collect()
        print(f"Free memory after running gc.collect(): {gc.mem_free()}")

        while True:
            hrs.value(
                hstart
                * uv(
                    -time.swe_localtime().hour * pi / 6
                    - time.swe_localtime().minute * pi / 360
                ),
                YELLOW,
            )
            mins.value(mstart * uv(-time.swe_localtime().minute * pi / 30), YELLOW)
            secs.value(sstart * uv(-time.swe_localtime().second * pi / 30), RED)
            dial.text(
                "{} {} {}".format(
                    days[time.swe_localtime().weekday()],
                    time.swe_localtime().day,
                    months[time.swe_localtime().month - 1],
                )
            )
            refresh(ssd)

            current_hour, prices_today, prices_tomorrow = utils.update_display(
                gui,
                prices_today,
                prices_tomorrow,
                current_hour,
                api,
                time.swe_localtime(),
            )
            pytime.sleep(1)


if __name__ == "__main__":
    main()
