"""Custom integration to integrate Home Easy compatible HVAC with Home Assistant."""
from homeeasy.HomeEasyLibLocal import HomeEasyLibLocal
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_IP,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class UpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, ip: str) -> None:
        """Initialize."""
        self._ip = ip
        self._api = HomeEasyLibLocal()
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        await self._api.disconnect()
        await self._api.connect(self._ip)
        self.state = await self._api.request_status_async()
        return self.state

    async def send(self):
        """Send state to device."""
        await self._api.disconnect()
        await self._api.connect(self._ip)
        await self._api.send(self.state)
