"""Constants for the Home Easy HVAC Local integration"""
# Base component constants
NAME = "Home Easy HVAC Local"
DOMAIN = "homeeasy_local"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "1.0.0"
ATTRIBUTION = ""
ISSUE_URL = "https://github.com/ki0ki0/homeeasy_ha_local/issues"

# Icons
ICON = "mdi:air-conditioner"

# Platforms
CLIMATE = "climate"
SELECT = "select"
PLATFORMS = [CLIMATE, SELECT]


# Configuration and options
CONF_IP = "ip"


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
