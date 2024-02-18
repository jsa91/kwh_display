"""
FÖRKLARA ALLT
"""

import gc
from price import ElectricityPriceAPI


def main():
    """
    Initialise classes for fetching spot prices and displaying objects.
    Run scheduling with clock.
    """

    api = ElectricityPriceAPI()
    api.get_prices()

    gc.collect()
    print(f"Free memory after running gc.collect(): {gc.mem_free()}")

    import time
    import machine
    import ujson
    from ili9341 import GUI
    from gui.core.nanogui import refresh
    from gui.color_setup import ssd
    from gui.core.colors import RED, YELLOW

    with open("prices.json", "r") as f:
        prices = ujson.load(f)

    prices_today = prices[0][str(time.localtime()[0:3])] if prices[0] else None
    prices_tomorrow = (
        prices[1][str(time.localtime(time.time() + 86400)[:3])]
        if len(prices) > 1
        else None
    )

    gui = GUI()

    current_hour = time.localtime()[3]
    gui.plot_prices(prices_today, prices_tomorrow)
    gui.set_price(current_hour, prices_today)
    gui.set_arrow(current_hour)
    uv, pi, days, months, dial, hrs, mins, secs, hstart, mstart, sstart = (
        gui.set_clock()
    )

    while True:
        t = time.localtime()
        hrs.value(hstart * uv(-t[3] * pi / 6 - t[4] * pi / 360), YELLOW)
        mins.value(mstart * uv(-t[4] * pi / 30), YELLOW)
        secs.value(sstart * uv(-t[5] * pi / 30), RED)
        dial.text("{} {} {}".format(days[t[6]], t[2], months[t[1] - 1]))
        refresh(ssd)

        hh = t[3]

        if hh != current_hour:

            if hh == 0:  # Tomorrows prices becomes todays prices when day changes
                prices_today = prices_tomorrow
                gui.plot_prices(prices_today, prices_tomorrow=None)

            elif (
                hh == 14
            ):  # Restart to fetch tomorrows prices due to memory allocation limitations
                machine.soft_reset()

            gui.set_price(hh, prices_today)  # Display price of current hour
            gui.set_arrow(
                hh
            )  # Set green arrow above x-axis integer to demonstrate current hour

        current_hour = hh

        time.sleep(1)


if __name__ == "__main__":
    main()
