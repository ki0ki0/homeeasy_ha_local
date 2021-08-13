"""BlueprintEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CLIMATE, CONF_IP, DOMAIN, NAME, VERSION, ATTRIBUTION


class Entity(CoordinatorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def name(self) -> str:
        """Return the name of the thermostat, if any."""
        return f"{DOMAIN}({self.config_entry.data.get(CONF_IP)})"
