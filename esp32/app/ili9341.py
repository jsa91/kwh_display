"""
Initialise drivers for hardware ILI9341 display.
"""

import cmath
from gui.fonts import arial10, arial35, freesans20
from gui.core.writer import CWriter
from gui.core.fplot import CartesianGraph, TSequence
from gui.core.nanogui import refresh
from gui.widgets.label import Label
from gui.core.colors import WHITE, BLACK, GREY, RED, GREEN, YELLOW
from gui.widgets.dial import Dial, Pointer
from gui.color_setup import ssd


class GUI:
    """
    Class that instantiate graphical objects on the display.
    """

    def __init__(self):
        # type: () -> None
        """
        Constructor
        """
        y_axis_division = [249, 225, 202, 179, 155]
        x_axis_division = [15, 30, 48, 66, 83, 98, 115, 133, 150, 168, 186, 204]
        arrows_division = [
            15,
            22,
            30,
            39,
            48,
            57,
            66,
            75,
            83,
            92,
            101,
            110,
            118,
            128,
            136,
            145,
            153,
            163,
            171,
            180,
            189,
            198,
            207,
            218,
        ]
        self.arrows = {}

        self.ssd = ssd
        refresh(self.ssd, True)  # Clear any prior image

        Label(
            CWriter(self.ssd, freesans20, WHITE, BLACK, verbose=False),
            2,
            71,
            "kwh display",
            align=2,
        )
        Label(
            CWriter(self.ssd, arial10, RED, BLACK, verbose=False),
            122,
            153,
            "Idag",
            align=2,
        )
        Label(
            CWriter(self.ssd, arial10, YELLOW, BLACK, verbose=False),
            122,
            183,
            "Imorgon",
            align=2,
        )
        Label(
            CWriter(self.ssd, freesans20, WHITE, BLACK, verbose=False),
            90,
            158,
            "kr/kWh",
            align=2,
        )
        self.wri = CWriter(ssd, arial10, WHITE, BLACK, verbose=False)
        self.graph = CartesianGraph(
            self.wri,
            135,
            15,
            xorigin=12,
            yorigin=2,
            height=140,
            width=210,
            fgcolor=WHITE,
            gridcolor=GREY,
            xdivs=12,
            ydivs=12,
        )
        self.ts_red = TSequence(self.graph, RED, 24, 0, 5)
        self.ts_yellow = TSequence(self.graph, YELLOW, 24, 0, 5)
        self.color_label = Label(
            CWriter(self.ssd, arial35, GREEN, BLACK, verbose=False),
            40,
            105,
            "Normalt",
            align=2,
        )
        self.price_label = Label(
            CWriter(self.ssd, freesans20, WHITE, BLACK, verbose=False),
            90,
            115,
            "0.00",
            align=2,
        )

        for x_label, x_axis_division in enumerate(x_axis_division):
            Label(self.wri, 289, x_axis_division, str((x_label * 2)), align=2)

        for y_label, y_axis_division in enumerate(y_axis_division):
            Label(self.wri, y_axis_division, 4, str((y_label)), align=2)

        for hour, arrow in enumerate(arrows_division):
            arrow_label = Label(self.wri, 279, arrow, "^", fgcolor=BLACK, align=2)
            self.arrows[f"arrow_{hour}"] = arrow_label

    def plot_prices(self, prices_today, prices_tomorrow):
        # type: (list, list) -> None
        """
        Plot spot prices in the graph

        Args:
            prices_today (dict): Todays spot prices fetched from api.
            prices_tomorrow (dict): Tomorrows spot prices fetched from api.
        """
        for today, tomorrow in zip(
            prices_today,
            prices_tomorrow if prices_tomorrow else [None] * len(prices_today),
        ):
            self.graph.clear()
            self.ts_red.add(today)
            if tomorrow is not None:
                self.ts_yellow.add(tomorrow)

        refresh(self.ssd)

    def set_price(self, current_hour, prices_today):
        # type: (int, dict) -> None
        """
        Set dynamical objects on the display, showing cost and price.

        Args:
            current_hour (int): Hour now
            prices_today (dict): Spot prices current day
        """
        price_levels = ("Billigt", "Normalt", "Dyrt")

        if prices_today[current_hour] < 0.5:
            color = GREEN
            price = price_levels[0]
        elif 0.5 <= prices_today[current_hour] < 1.5:
            color = YELLOW
            price = price_levels[1]
        else:
            color = RED
            price = price_levels[2]

        cost = prices_today[current_hour]
        cost = "{:.1f}".format(cost) if cost >= 10 else "{:.2f}".format(cost)

        self.color_label.value(text=price, fgcolor=color)
        self.price_label.value(text=cost)

        refresh(self.ssd)

    def set_arrow(self, current_hour):
        # type: (int) -> None
        """
        Set indicator arrow above x-axis integer to demonstrate current hour

        Args:
            current_hour (int): Hour now
        """
        if current_hour == 0:
            self.arrows["arrow_23"].value(fgcolor=BLACK)
        else:
            self.arrows[f"arrow_{current_hour - 1}"].value(fgcolor=BLACK)

        self.arrows[f"arrow_{current_hour}"].value(fgcolor=GREEN)
        refresh(self.ssd)

    def set_clock(self):
        # type: () -> tuple
        """
        Instantiate variables needed to display analog clock.

        Returns:
            tuple: analog clock parameters
        """
        uv = lambda phi: cmath.rect(1, phi)
        pi = cmath.pi
        days = (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        )
        months = (
            "Jan",
            "Feb",
            "March",
            "April",
            "May",
            "June",
            "July",
            "Aug",
            "Sept",
            "Oct",
            "Nov",
            "Dec",
        )

        dial = Dial(
            self.wri, 25, 15, height=90, ticks=12, bdcolor=WHITE, label=90, pip=False
        )
        hrs = Pointer(dial)
        mins = Pointer(dial)
        secs = Pointer(dial)

        hstart = 0 + 0.7j
        mstart = 0 + 0.92j
        sstart = 0 + 0.92j

        return uv, pi, days, months, dial, hrs, mins, secs, hstart, mstart, sstart
