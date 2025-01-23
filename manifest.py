# kwh_display
package("drivers", base_path="$(MPY_DIR)/kwh_display/esp32")
package("ftp", base_path="$(MPY_DIR)/kwh_display/esp32")
package("gui", base_path="$(MPY_DIR)/kwh_display/esp32")
package("app", base_path="$(MPY_DIR)/kwh_display/esp32")
module("main.py", base_path="$(MPY_DIR)/kwh_display/esp32")
require("datetime")

