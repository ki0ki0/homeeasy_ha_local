"""Custom integration to integrate Home Easy compatible HVAC with Home Assistant."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import (
    REQUEST_REFRESH_DEFAULT_COOLDOWN,
    REQUEST_REFRESH_DEFAULT_IMMEDIATE,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeeasy.DeviceState import DeviceState
from homeeasy.HomeEasyLibLocal import HomeEasyLibLocal

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

    state: DeviceState = None

    def __init__(self, hass: HomeAssistant, ip: str) -> None:
        """Initialize."""
        self._ip = ip
        self._api = HomeEasyLibLocal(hass.loop, self._update_callback)
        self.platforms = []
        self._connected = False

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            request_refresh_debouncer=Debouncer(
                hass,
                _LOGGER,
                cooldown=60,
                immediate=False,
                function=self.async_refresh,
            ),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            if not self._connected:
                await self._api.connect(self._ip)
                self._connected = True

            await self._api.request_status_async()
        except Exception as ex:
            _LOGGER.error("Error updating data: %s", str(ex))
            self._connected = False
            raise UpdateFailed(f"Error communicating with API: {str(ex)}")

    async def _update_callback(self, state):
        """Update data via library."""
        try:
            self.state = state
            self.async_set_updated_data(state)
        except Exception as ex:
            _LOGGER.error("Error in update callback: %s", str(ex))

    async def send(self, state):
        """Send state to device."""
        if state is None:
            _LOGGER.error("Cannot send None state")
            return

        try:
            if not self._connected:
                _LOGGER.warning("Reconnecting to device...")
                await self._api.connect(self._ip)
                self._connected = True

            await self._api.send(state)
        except Exception as ex:
            self._connected = False
            _LOGGER.error("Error sending state to device: %s", str(ex))
            raise HomeAssistantError(f"Failed to send state to device: {str(ex)}")
