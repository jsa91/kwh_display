"""
boot.py -- run on boot-up
"""

import network
import ujson
import ntptime
import utime
import machine
import gc
import webrepl
import os


def wifi():
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


def ntp():
    """
    Sync UTC time with NTP
    """

    print("Synchronizing time with NTP server...")
    ntptime.timeout = 3
    for _ in range(3):  # Try sync time three times before reset
        try:
            ntptime.settime()
            break
        except OSError as e:
            print(f"Time synchronization failed: {e}\nTrying again in 15 sec...")
            utime.sleep(15)
    else:
        print("Time synchronization failed, resetting...")
        machine.soft_reset()

    ntp_time = utime.localtime()
    print("UTC time synchronized successfully:")
    print(
        f"{ntp_time[0]:04d}-{ntp_time[1]:02d}-{ntp_time[2]:02d} {ntp_time[3]:02d}:{ntp_time[4]:02d}:{ntp_time[5]:02d}"
    )


if "config.json" in os.listdir():
    wifi()
    ntp()
    webrepl.start()  # Start webrepl with password 'timerepl'
    gc.collect()
    print(f"Free memory after running gc.collect(): {gc.mem_free()}")
else:
    hotspot()
    import sys
    from ftp import uftpd

    print("Config file missing. Access the through FTP to manage filesystem.")
    sys.exit()
