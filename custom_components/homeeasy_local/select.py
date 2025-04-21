"""Climate platform for Home Easy HVAC Local."""
from homeeasy.DeviceState import HorizontalFlowMode, VerticalFlowMode

from homeassistant.components.select import SelectEntity

from .const import DOMAIN, SELECT
from .entity import Entity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            HomeEasyHvacLocalHorizontal(coordinator, entry),
            HomeEasyHvacLocalVertical(coordinator, entry),
        ]
    )


SUPPORT_HORIZONTAL = {
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


SUPPORT_VERTICAL = {
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
    def name(self) -> str:
        """Return the name of the thermostat, if any."""
        return f"{super().name}_{SELECT}_Vertical"

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        return list(SUPPORT_VERTICAL.keys())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        state = self.coordinator.state
        state.flowVerticalMode = SUPPORT_VERTICAL[option]
        await self.coordinator.send(state)

    @property
    def current_option(self) -> str:
        """Return the selected entity option to represent the entity state."""
        if self.coordinator.state is None:
            return None

        for (key, value) in SUPPORT_VERTICAL.items():
            if self.coordinator.state.flowVerticalMode == value:
                return key
        return None


class HomeEasyHvacLocalHorizontal(Entity, SelectEntity):
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
        state = self.coordinator.state
        state.flowHorizontalMode = SUPPORT_HORIZONTAL[option]
        await self.coordinator.send(state)

    @property
    def current_option(self) -> str:
        """Return the selected entity option to represent the entity state."""
        if self.coordinator.state is None:
            return None
            
        for (key, value) in SUPPORT_HORIZONTAL.items():
            if self.coordinator.state.flowHorizontalMode == value:
                return key
        return None
