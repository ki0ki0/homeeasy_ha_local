"""Climate platform for Home Easy HVAC Local."""

from __future__ import annotations

import logging
from typing import Final

from homeassistant.components.select import SelectEntity
from homeassistant.exceptions import HomeAssistantError
from homeeasy.DeviceState import DeviceState, HorizontalFlowMode, VerticalFlowMode

from .const import DOMAIN, SELECT
from .entity import Entity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            HomeEasyHvacLocalHorizontal(coordinator, entry),
            HomeEasyHvacLocalVertical(coordinator, entry),
        ]
    )


SUPPORT_HORIZONTAL: Final = {
    "Stop": HorizontalFlowMode.Stop,
    "Swing": HorizontalFlowMode.Swing,
    "Left": HorizontalFlowMode.Left,
    "Left_Center": HorizontalFlowMode.Left_Center,
    "Center": HorizontalFlowMode.Center,
    "Right_Center": HorizontalFlowMode.Right_Center,
    "Right": HorizontalFlowMode.Right,
    "Left_Right": HorizontalFlowMode.Left_Right,
    "Swing_Wide": HorizontalFlowMode.Swing_Wide,
}


SUPPORT_VERTICAL: Final = {
    "Stop": VerticalFlowMode.Stop,
    "Swing": VerticalFlowMode.Swing,
    "Top": VerticalFlowMode.Top,
    "Top_Center": VerticalFlowMode.Top_Center,
    "Center": VerticalFlowMode.Center,
    "Bottom_Center": VerticalFlowMode.Bottom_Center,
    "Bottom": VerticalFlowMode.Bottom,
}


class HomeEasyHvacLocalVertical(Entity, SelectEntity):
    @property
    def _state(self) -> DeviceState | None:
        """Return coordinator state with proper typing."""
        return self.coordinator.state

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True

    @property
    def name(self) -> str:
        """Return the name of the thermostat, if any."""
        return f"{super().name}_{SELECT}_Vertical"

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        return list(SUPPORT_VERTICAL.keys())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in SUPPORT_VERTICAL:
            raise HomeAssistantError(
                f"Invalid vertical mode option: {option}. Valid options are: {', '.join(SUPPORT_VERTICAL.keys())}"
            )

        state = self._state
        if state is None:
            _LOGGER.warning("Cannot set vertical mode - state is None")
            return

        try:
            state.flowVerticalMode = SUPPORT_VERTICAL[option]
            await self.coordinator.send(state)
            await self.coordinator.async_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set vertical mode: %s", str(ex))
            raise HomeAssistantError(f"Failed to set vertical mode: {str(ex)}")

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        state = self._state
        if state is None:
            return None

        try:
            for key, value in SUPPORT_VERTICAL.items():
                if state.flowVerticalMode == value:
                    return key
        except Exception as ex:
            _LOGGER.error("Error getting vertical mode: %s", str(ex))
        return None


class HomeEasyHvacLocalHorizontal(Entity, SelectEntity):
    @property
    def _state(self) -> DeviceState | None:
        """Return coordinator state with proper typing."""
        return self.coordinator.state

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{super().unique_id}_Horizontal"

    @property
    def name(self) -> str:
        """Return the name of the thermostat, if any."""
        return f"{super().name}_{SELECT}_Horizontal"

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        return list(SUPPORT_HORIZONTAL.keys())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in SUPPORT_HORIZONTAL:
            raise HomeAssistantError(
                f"Invalid horizontal mode option: {option}. Valid options are: {', '.join(SUPPORT_HORIZONTAL.keys())}"
            )

        state = self._state
        if state is None:
            _LOGGER.warning("Cannot set horizontal mode - state is None")
            return

        try:
            state.flowHorizontalMode = SUPPORT_HORIZONTAL[option]
            await self.coordinator.send(state)
            await self.coordinator.async_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set horizontal mode: %s", str(ex))
            raise HomeAssistantError(f"Failed to set horizontal mode: {str(ex)}")

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        state = self._state
        if state is None:
            return None

        try:
            for key, value in SUPPORT_HORIZONTAL.items():
                if state.flowHorizontalMode == value:
                    return key
        except Exception as ex:
            _LOGGER.error("Error getting horizontal mode: %s", str(ex))
        return None
