# kwh_display

*kwh_display* is a project developed in MicroPython aimed at creating a compact display solution using an ESP32 and an ILI9341 screen. The primary functionality of this project is to fetch electricity price data via API and display it on the screen.

![IMG_2749](https://github.com/user-attachments/assets/1165a0df-f645-466b-9224-a323dd0af6c2)

## Features

- Fetches electricity price data daily when available from an API. <span style="float: right;"><a href="https://www.elprisetjustnu.se"><img src="https://ik.imagekit.io/ajdfkwyt/hva-koster-strommen/elpriser-tillhandahalls-av-elprisetjustnu_ttNExOIU_.png" alt="Elpriser tillhandahålls av Elpriset just nu.se" width="200" height="45"></a></span>
- Inspired by the project [PowerDisplayESPHome](https://github.com/johannyren/PowerDisplayESPHome) but developed without any backend dependencies.
- Displays the current day's price alongside tomorrow's price.
- Shows the electricity price in kWh/SEK for the current hour.
- Allows users to select a bidding area (SE 1-4).
<!---
- Allows users to customize the price interval.
-->

This project aims to provide a standalone solution for monitoring electricity prices without relying on external services.

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
<img src="https://github.com/user-attachments/assets/355e2bc7-83c0-4814-930c-5a3256996608" width="450" height="600">

## Casing

```/kwh_display/casing``` holds two STL files avalible for 3D printing the display casing.

## ESP32

To use *kwh_display*, start by flashing the ESP32 with firmware `build-ESP32_GENERIC_250127.bin`, which is compiled from the [MicroPython](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html) repository.


Erase and the flash the ESP32 using [esptool](https://github.com/espressif/esptool).

```
esptool.py --port /dev/ttyUSB0 erase_flash && esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 build-ESP32_GENERIC_250127.bin
```
<!---
Edit ```/kwh_display/config.json``` to match your preferred settings. You can customize the price interval to your preference (float). The default settings are explained in the table below.

| Price    | Default            |
| -------- | -------------------|
| Billigt  | Price < 0.5        |
| Normalt  | 0.5 <= Price < 1.5 |
| Dyrt     | 1.5 <= Price       |

The case *Dyrt* is handled by an 'else' statement.

**Please note that your WiFi password will be stored in plain text. Proceed with caution.**
```json
{
  "ssid": "linusgarden-IoT",
  "password": "C5DT_F+BDXfsRuDd%8#6",
  "zone": "SE3",
  "url": "http://www.elprisetjustnu.se",
  "api": "/api/v1/prices/",
  "billigt<": 0.5,
  "normalt<": 1.5
}
```
-->

Edit ```/kwh_display/config.json``` to match your preferred settings.

**Please note that your WiFi password will be stored in plain text. Proceed with caution.**
```json
{
  "ssid": "YourSSID",
  "password": "YourPassword",
  "zone": "SE3",
  "url": "http://www.elprisetjustnu.se",
  "api": "/api/v1/prices/"
}
```

When the *kwh_display*  boots for the first time it will deploy a hotspot with the SSID `kwh_display` and host an FTP file server. Access the file server using your preferred method at `ftp://192.168.4.1/`. After adding `config.json` to the root of the file system, repower the device.

## Troubleshooting
If *kwh_display* does not boot correctly or if `Config Error!` is showing on the display, connect the ESP32 to a serial console. Reboot and analyze the output.

```
screen /dev/ttyUSB0 115200
```
The ESP32 has booted correctly if you see output similar to the following in the console:

```console
Boot sequence completed @ <TIME>
Free memory after running gc.collect(): <MEM>
```

## Known Limitations

Currently, it is not possible to adjust the offset price according to power tariffs. Additionally, it is not possible to customize the price levels (Billigt, Normalt, Dyrt) to your own preferences. Hopefully, this feature will be added in the future.

## Development

The *kwh_display* firmware is compiled from [MicroPython](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html) using [mpbuild](https://github.com/mattytrentini/mpbuild). `/kwh_display/esp32` code has been “frozen” into the firmware to optimize memory allocation via the `/kwh_display/manifest.py` file. Drivers were developed by [peterhinch](https://github.com/peterhinch/micropython-nano-gui). The FTP server was developed by [robert-hh](https://github.com/robert-hh/FTP-Server-for-ESP8266-ESP32-and-PYBD).
