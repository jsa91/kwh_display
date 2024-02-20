# kwh_display (under development)

*kwh_display* is a project developed in MicroPython aimed at creating a compact display solution using an ESP32 and an ILI9341 screen. The primary functionality of this project is to fetch electricity price data via API and display it on the screen.

## Features

- Fetches electricity price data daily at 14:00 CET from the [Elpriset just nu](https://www.elprisetjustnu.se/elpris-api) API.
- Displays the current day's price alongside tomorrow's price.
- Shows the electricity price in kWh/SEK for the current hour.
- Allows users to select a bidding area (SE 1-4) according to their preference.
- Inspired by the project [PowerDisplayESPHome](https://github.com/johannyren/PowerDisplayESPHome) but developed without any backend dependencies.

This project aims to provide a standalone solution for monitoring electricity prices without relying on external servers or services.

<!---BILD-->

## ESP32

To use this repository, start by flashing the ESP32 with [MicroPython](https://docs.MicroPython.org/en/latest/esp32/tutorial/intro.html). The latest tested firmware build is `ESP32_GENERIC-20231227-v1.22.0.bin`.

For convenient file management and the ability to copy to and from the ESP32, consider using [rshell](https://github.com/dhylands/rshell). It also doubles as a terminal emulator and provides access to the regular REPL.

## ILI9341

Below is the wiring schematic for connecting the ESP32 to the ILI9341 display (2.8 TFT SPI 240x320).

```
ESP   SSD
---------
3v3   VCC
3v3   LED
GND   GND
IO25  DC
IO26  CS
IO27  RESET
IO14  SCK
IO13  MOSI
IO12  MISO
```

## Casing

```/kwh_display/casing``` holds two STL files avalible for 3D printing the display casing.

<!---BILD-->

## How To

TBD

## Known limitations 

TBD

