"""Adds config flow for Home Easy HVAC Local."""
import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeeasy.HomeEasyLibLocal import HomeEasyLibLocal
import voluptuous as vol

from .const import (
    CONF_IP,
    DOMAIN,
    PLATFORMS,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Home Easy HVAC Local."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            _LOGGER.debug(f"IP {user_input[CONF_IP]}")
            valid = await self._test_connection(user_input[CONF_IP])
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_IP], data=user_input
                )
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_IP): str}),
            errors=self._errors,
        )

    async def _test_connection(self, ip):
        """Return true if credentials is valid."""
        try:
            client = HomeEasyLibLocal(self.hass.loop, None)
            await client.connect(ip)
            await client.request_status_async()
            await client.disconnect()
            return True
        except Exception:  # pylint: disable=broad-except
            pass
        return False
