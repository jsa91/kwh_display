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
        time = SweTime()

        api = ElectricityPriceAPI(time.utc_time())
        prices_today, prices_tomorrow, dst_offset = api.get_prices(time.utc_time())

        print(
            f"Time offset today is {dst_offset} hours, {'DST is effect.' if dst_offset == 2 else 'CET in effect.'}"
        )

        print("Preparing display...")

        # Calculate current 15-minute interval (0-95)
        current_time = time.swe_localtime(dst_offset)
        current_15min = (current_time.hour * 4) + (current_time.minute // 15)

        gui = GUI()
        gui.plot_prices(prices_today, prices_tomorrow)
        gui.set_price(current_15min, prices_today)
        gui.set_arrow(current_time.hour)
        uv, pi, days, months, dial, hrs, mins, secs, hstart, mstart, sstart = (
            gui.set_clock()
        )

        print(
            f"Boot sequence completed @ {time.swe_localtime(dst_offset).year}-{time.swe_localtime(dst_offset).month}-{time.swe_localtime(dst_offset).day} {time.swe_localtime(dst_offset).hour}:{time.swe_localtime(dst_offset).minute}:{time.swe_localtime(dst_offset).second}"
        )

        gc.collect()
        print(f"Free memory after running gc.collect(): {gc.mem_free()}")

        while True:
            hrs.value(
                hstart
                * uv(
                    -time.swe_localtime(dst_offset).hour * pi / 6
                    - time.swe_localtime(dst_offset).minute * pi / 360
                ),
                YELLOW,
            )
            mins.value(
                mstart * uv(-time.swe_localtime(dst_offset).minute * pi / 30), YELLOW
            )
            secs.value(
                sstart * uv(-time.swe_localtime(dst_offset).second * pi / 30), RED
            )
            dial.text(
                "{} {} {}".format(
                    days[time.swe_localtime(dst_offset).weekday()],
                    time.swe_localtime(dst_offset).day,
                    months[time.swe_localtime(dst_offset).month - 1],
                )
            )
            refresh(ssd)

            current_15min, prices_today, prices_tomorrow = utils.update_display(
                gui,
                prices_today,
                prices_tomorrow,
                current_15min,
                api,
                time.swe_localtime(dst_offset),
            )
            pytime.sleep(1)


if __name__ == "__main__":
    main()
