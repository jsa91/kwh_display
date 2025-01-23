# kwh_display

*kwh_display* is a project developed in MicroPython aimed at creating a compact display solution using an ESP32 and an ILI9341 screen. The primary functionality of this project is to fetch electricity price data via API and display it on the screen.

![kwh_display](https://github.com/user-attachments/assets/ac35568e-17c2-4a92-991a-805e1c3b35c9)

## Features

- Fetches electricity price data daily at 14:00 CET from the [Elpriset just nu](https://www.elprisetjustnu.se/elpris-api) API.
- Displays the current day's price alongside tomorrow's price.
- Shows the electricity price in kWh/SEK for the current hour.
- Allows users to select a bidding area (SE 1-4) according to their preference.
- Inspired by the project [PowerDisplayESPHome](https://github.com/johannyren/PowerDisplayESPHome) but developed without any backend dependencies.

This project aims to provide a standalone solution for monitoring electricity prices without relying on external servers or services.

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
![wiring](https://github.com/user-attachments/assets/355e2bc7-83c0-4814-930c-5a3256996608)

## Casing

```/kwh_display/casing``` holds two STL files avalible for 3D printing the display casing.

## How-to

Begin by erasing the flash on the ESP32 using [esptool](https://github.com/espressif/esptool).

```
esptool.py --port /dev/ttyUSB0 erase_flash
```

Deploy MicroPython firmware onto the board.

```
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20231227-v1.22.0.bin
```

Clone the repository and edit ```/kwh_display/esp32/config.json``` to match your preferred settings.

**Please note that your WiFi password will be stored in plain text. Proceed with caution.**
```python
{
  "ssid": "YourSSID",
  "password": "YourPassword",
  "zone": "SE3", # Bidding area
  "url": "http://www.elprisetjustnu.se",
  "api": "/api/v1/prices/"
}
```
Enter ```rshell``` and connect to the ESP32.

```
connect serial /dev/ttyUSB0
```

From ```kwh_display>```, copy the contents of ```esp32/``` onto the board.
```
rsync -a esp32/. /pyboard/
```

Start the display by typing ```repl``` followed by ```Ctrl+D```, or by repowering the device. 

## Alternative Handling of Config File
If properties of the ```config.json``` are currently unknown or if you need to add the file later, you can do so using FTP.

Ensure you delete ```config.json``` from ```/kwh_display/esp32/``` before copying the contents of ```esp32/``` onto the board.

When the display boots without the config file present, it will deploy a hotspot with SSID ```kwh_display``` and FTP file server functionality. Access the file server in your preferred way at ```ftp://192.168.4.1/```. After adding the config file to the file system, repower the device.



## Known Limitations

Due to memory allocation limitations, the display will reboot itself daily at 14:00 CET to fetch updated electricity prices.
Hopefully, these issues will be addressed in the future by implementing a [manifest](https://docs.micropython.org/en/latest/reference/manifest.html) file.

As of now, it is not possible to adjust the offset price according to power tariffs. Hopefully, this feature will be added in the future.

For maintenance and debugging a WebREPL server can be accessible at ```http://<device-ip>:8266/``` with password ```webrepl```. To conserve memory this server is disabled by default but can be enabled in ```boot.py``` file.

If there arises a need to change the WiFi SSID and password in the config file, it's recommended to reflash the device firmware and then make changes.
