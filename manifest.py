freeze("$(PORT_DIR)/modules")
include("$(MPY_DIR)/extmod/asyncio")

# Useful networking-related packages.
require("bundle-networking")

# Require some micropython-lib modules.
require("aioespnow")
require("dht")
require("ds18x20")
require("neopixel")
require("onewire")
require("umqtt.robust")
require("umqtt.simple")
require("upysh")

# kwh_display
package("drivers", base_path="$(MPY_DIR)/kwh_display/esp32")
package("ftp", base_path="$(MPY_DIR)/kwh_display/esp32")
package("gui", base_path="$(MPY_DIR)/kwh_display/esp32")
package("app", base_path="$(MPY_DIR)/kwh_display/esp32")
module("main.py", base_path="$(MPY_DIR)/kwh_display/esp32")
require("datetime")
require("ntptime")
require("urequests")
