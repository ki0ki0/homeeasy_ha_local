"""Climate platform for Home Easy HVAC Local."""
from homeeasy.DeviceState import DeviceState

from homeassistant.components.switch import SwitchEntity
#from homeassistant.const import Platform
from .const import DOMAIN, SWITCH
from .entity import Entity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([HomeEasyHvacLocalDisplay(coordinator, entry)])


class HomeEasyHvacLocalDisplay(Entity, SwitchEntity):
    @property
    def name(self) -> str:
        """Return the name of the thermostat, if any."""
        return f"{super().name}_{SWITCH}_Display"

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        state = self.coordinator.state
        return state.display 

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        state = self.coordinator.state
        state.display = True
        await self.coordinator.send(state)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        state = self.coordinator.state
        state.display = False
        await self.coordinator.send(state)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        state = self.coordinator.state
        return (
            super().available
            and hasattr(state, 'display')
        )
